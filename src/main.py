import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

from src.excel_handler import read_excel
from src.distance_calculator import get_distance_and_duration, DistanceLookupError
from src.scheduler import schedule_appointment, OutlookUnavailableError

PRIORITY_ORDER = {'High': 0, 'Medium': 1, 'Low': 2}
MEETING_DURATION_MINUTES = 60
DEFAULT_START_HOUR = 9


def build_schedule(df, api_key, start_date, meeting_duration=MEETING_DURATION_MINUTES):
    """
    Treats the first row as the starting location (e.g. the office), then visits the
    remaining clients ordered by Priority (High -> Medium -> Low). Each appointment is
    booked back-to-back, spaced out by the meeting duration plus the driving time from
    the previous stop, starting at DEFAULT_START_HOUR on start_date.

    Returns a list of dicts describing each planned appointment (without booking them).
    """
    if len(df) < 2:
        raise ValueError("Need at least one starting location and one client to schedule.")

    origin_row = df.iloc[0]
    clients = df.iloc[1:].copy()
    clients['_priority_rank'] = clients['Priority'].map(PRIORITY_ORDER)
    clients = clients.sort_values('_priority_rank', kind='stable')

    schedule = []
    current_time = start_date.replace(hour=DEFAULT_START_HOUR, minute=0, second=0, microsecond=0)
    origin = origin_row['Address']

    for _, row in clients.iterrows():
        destination = row['Address']
        distance_text, travel_minutes = get_distance_and_duration(api_key, origin, destination)

        if schedule:
            current_time += timedelta(minutes=meeting_duration + travel_minutes)

        schedule.append({
            'client_name': row['ClientName'],
            'address': destination,
            'priority': row['Priority'],
            'distance_from_previous': distance_text,
            'travel_minutes_from_previous': travel_minutes,
            'start_time': current_time,
            'duration_minutes': meeting_duration,
        })
        origin = destination

    return schedule


def main():
    load_dotenv()
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    excel_file = os.getenv('CLIENT_LIST_FILE', 'Client List/Clients.xlsx')
    start_date = datetime.now() + timedelta(days=1)  # schedule for the next business day

    df = read_excel(excel_file)

    try:
        schedule = build_schedule(df, api_key, start_date)
    except DistanceLookupError as exc:
        print(f"Error calculating distances: {exc}")
        return

    for item in schedule:
        print(
            f"{item['client_name']} ({item['priority']}) at {item['address']} - "
            f"{item['distance_from_previous']} / {item['travel_minutes_from_previous']} min away - "
            f"starts {item['start_time']:%Y-%m-%d %H:%M}"
        )
        try:
            schedule_appointment(
                subject=f"Meeting with {item['client_name']}",
                start_time=item['start_time'],
                duration=item['duration_minutes'],
                location=item['address'],
                body=f"Discuss with {item['client_name']} (Priority: {item['priority']})",
            )
        except OutlookUnavailableError as exc:
            print(f"Could not schedule '{item['client_name']}': {exc}")


if __name__ == "__main__":
    main()
