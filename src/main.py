import argparse
import logging
from datetime import datetime, timedelta

import pandas as pd

from src.config import load_config
from src.excel_handler import add_priority, read_excel, save_excel
from src.distance_calculator import DistanceLookupError
from src.geocoder import validate_addresses, AddressValidationError
from src.logging_setup import setup_logging
from src.router import order_clients
from src.scheduler import schedule_appointment, get_existing_appointments, OutlookUnavailableError

logger = logging.getLogger(__name__)

MEETING_DURATION_MINUTES = 60
DEFAULT_START_HOUR = 9
DEFAULT_END_HOUR = 17
DEFAULT_LUNCH_START_HOUR = 12
DEFAULT_LUNCH_END_HOUR = 13


def _at_hour(base_date, hour):
    return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)


def _overlaps(start_a, end_a, start_b, end_b):
    return start_a < end_b and end_a > start_b


def _push_past_conflicts(start_time, duration, lunch_start, lunch_end, existing_appointments):
    """Advances start_time past the lunch window and any existing calendar appointments it
    would overlap, re-checking until a clear slot is found."""
    moved = True
    while moved:
        moved = False
        end_time = start_time + timedelta(minutes=duration)

        if _overlaps(start_time, end_time, lunch_start, lunch_end):
            start_time = lunch_end
            moved = True
            continue

        for ex_start, ex_end in existing_appointments:
            if _overlaps(start_time, end_time, ex_start, ex_end):
                start_time = ex_end
                moved = True
                break

    return start_time


def build_schedule(
    df,
    api_key,
    start_date,
    meeting_duration=MEETING_DURATION_MINUTES,
    start_hour=DEFAULT_START_HOUR,
    end_hour=DEFAULT_END_HOUR,
    lunch_start_hour=DEFAULT_LUNCH_START_HOUR,
    lunch_end_hour=DEFAULT_LUNCH_END_HOUR,
    existing_appointments=None,
):
    """
    Treats the first row as the starting location (e.g. the office). Validates every
    address up front, then visits the remaining clients ordered by Priority tier
    (High -> Medium -> Low), and by nearest-neighbor distance within each tier. Each
    appointment is booked back-to-back, spaced out by its duration plus the driving time
    from the previous stop, skipping the lunch window and any existing calendar
    appointments. Clients that don't fit before end_hour are returned as unscheduled
    rather than booked late.

    Returns (schedule, unscheduled): schedule is a list of dicts describing each planned
    appointment (without booking them); unscheduled is a list of client dicts that
    couldn't be fit into the business day.
    """
    if len(df) < 2:
        raise ValueError("Need at least one starting location and one client to schedule.")

    existing_appointments = existing_appointments or []

    origin_row = df.iloc[0]
    clients_df = df.iloc[1:]

    addresses = [origin_row['Address']] + clients_df['Address'].tolist()
    bad_addresses = validate_addresses(api_key, addresses)
    if bad_addresses:
        raise AddressValidationError(
            "Could not validate the following address(es): " + ", ".join(bad_addresses)
        )

    clients = []
    for _, row in clients_df.iterrows():
        has_duration = 'Duration' in clients_df.columns and pd.notna(row.get('Duration'))
        clients.append({
            'client_name': row['ClientName'],
            'address': row['Address'],
            'priority': row['Priority'],
            'duration_minutes': int(row['Duration']) if has_duration else meeting_duration,
        })

    ordered = order_clients(clients, origin_row['Address'], api_key)

    day_start = _at_hour(start_date, start_hour)
    day_end = _at_hour(start_date, end_hour)
    lunch_start = _at_hour(start_date, lunch_start_hour)
    lunch_end = _at_hour(start_date, lunch_end_hour)

    schedule = []
    unscheduled = []
    current_time = day_start
    previous_duration = 0

    for i, client in enumerate(ordered):
        duration = client['duration_minutes']
        travel_minutes = client['travel_minutes_from_previous'] if i > 0 else 0

        if i > 0:
            current_time += timedelta(minutes=previous_duration + travel_minutes)

        current_time = _push_past_conflicts(
            current_time, duration, lunch_start, lunch_end, existing_appointments
        )
        previous_duration = duration

        if current_time + timedelta(minutes=duration) > day_end:
            unscheduled.append(client)
            continue

        schedule.append({
            'client_name': client['client_name'],
            'address': client['address'],
            'priority': client['priority'],
            'distance_from_previous': client['distance_from_previous'],
            'travel_minutes_from_previous': client['travel_minutes_from_previous'],
            'start_time': current_time,
            'duration_minutes': duration,
        })

    return schedule, unscheduled


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Plan and book a day of client visits.")
    parser.add_argument(
        '--dry-run', action='store_true',
        help="Print the planned route without touching Outlook.",
    )
    parser.add_argument('--date', help="Date to schedule for (YYYY-MM-DD). Defaults to tomorrow.")
    parser.add_argument('--duration', type=int, help="Default meeting duration in minutes.")
    parser.add_argument('--file', help="Path to the client list Excel file.")
    parser.add_argument(
        '--set-priority', nargs=2, metavar=('CLIENT_NAME', 'PRIORITY'),
        help="Set a client's Priority (High/Medium/Low) in the Excel file and exit.",
    )
    return parser.parse_args(argv)


def _set_priority(config, client_name, priority):
    df = read_excel(config.client_list_file)
    try:
        add_priority(df, client_name, priority)
    except ValueError as exc:
        logger.error("Failed to set priority: %s", exc)
        print(exc)
        return
    save_excel(df, config.client_list_file)
    print(f"Updated {client_name}'s priority to {priority}.")


def main(argv=None):
    args = parse_args(argv)
    setup_logging()

    overrides = {}
    if args.duration:
        overrides['meeting_duration_minutes'] = args.duration
    if args.file:
        overrides['client_list_file'] = args.file
    config = load_config(overrides=overrides)

    if args.set_priority:
        client_name, priority = args.set_priority
        _set_priority(config, client_name, priority)
        return

    start_date = (
        datetime.strptime(args.date, '%Y-%m-%d') if args.date
        else datetime.now() + timedelta(days=1)
    )

    df = read_excel(config.client_list_file)

    existing_appointments = []
    if not args.dry_run:
        try:
            existing_appointments = get_existing_appointments(start_date)
        except OutlookUnavailableError as exc:
            logger.warning("Could not check existing calendar appointments: %s", exc)
            print(f"Could not check existing calendar appointments: {exc}")

    try:
        schedule, unscheduled = build_schedule(
            df,
            config.api_key,
            start_date,
            meeting_duration=config.meeting_duration_minutes,
            start_hour=config.start_hour,
            end_hour=config.end_hour,
            lunch_start_hour=config.lunch_start_hour,
            lunch_end_hour=config.lunch_end_hour,
            existing_appointments=existing_appointments,
        )
    except (DistanceLookupError, AddressValidationError) as exc:
        logger.error("Error building the schedule: %s", exc)
        print(f"Error building the schedule: {exc}")
        return

    for item in schedule:
        line = (
            f"{item['client_name']} ({item['priority']}) at {item['address']} - "
            f"{item['distance_from_previous']} / {item['travel_minutes_from_previous']} min away - "
            f"starts {item['start_time']:%Y-%m-%d %H:%M}"
        )
        print(line)
        logger.info(line)

        if args.dry_run:
            continue

        try:
            schedule_appointment(
                subject=f"Meeting with {item['client_name']}",
                start_time=item['start_time'],
                duration=item['duration_minutes'],
                location=item['address'],
                body=f"Discuss with {item['client_name']} (Priority: {item['priority']})",
            )
        except OutlookUnavailableError as exc:
            logger.error("Could not schedule '%s': %s", item['client_name'], exc)
            print(f"Could not schedule '{item['client_name']}': {exc}")

    if unscheduled:
        print("\nCould not fit the following clients into the day:")
        for client in unscheduled:
            print(f"  {client['client_name']} ({client['priority']}) at {client['address']}")


if __name__ == "__main__":
    main()
