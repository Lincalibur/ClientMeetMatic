from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.geocoder import AddressValidationError
from src.main import build_schedule, main, parse_args

DF = pd.DataFrame({
    'ClientName': ['Origin', 'ClientA', 'ClientB'],
    'Address': ['Start St', 'A St', 'B St'],
    'Priority': ['Low', 'High', 'Medium'],
})


def _client(name, priority, duration=60, travel_from_previous=0):
    return {
        'client_name': name,
        'address': f'{name} St',
        'priority': priority,
        'duration_minutes': duration,
        'distance_from_previous': '5 km',
        'travel_minutes_from_previous': travel_from_previous,
    }


@patch("src.main.order_clients")
@patch("src.main.validate_addresses")
def test_build_schedule_spaces_by_duration_and_travel(mock_validate, mock_order):
    mock_validate.return_value = []
    mock_order.return_value = [
        _client('ClientA', 'High', duration=60, travel_from_previous=0),
        _client('ClientB', 'Medium', duration=60, travel_from_previous=20),
    ]
    start = datetime(2030, 1, 1, 8, 0)

    schedule, unscheduled = build_schedule(DF, api_key="fake-key", start_date=start)

    assert unscheduled == []
    assert schedule[0]['start_time'].hour == 9
    gap = schedule[1]['start_time'] - schedule[0]['start_time']
    assert gap.total_seconds() / 60 == 80  # 60 min meeting + 20 min travel


@patch("src.main.order_clients")
@patch("src.main.validate_addresses")
def test_build_schedule_marks_overflow_as_unscheduled(mock_validate, mock_order):
    mock_validate.return_value = []
    mock_order.return_value = [
        _client('ClientA', 'High', duration=60, travel_from_previous=0),
        _client('ClientB', 'Medium', duration=60, travel_from_previous=30),
    ]
    start = datetime(2030, 1, 1, 8, 0)

    schedule, unscheduled = build_schedule(DF, api_key="fake-key", start_date=start, end_hour=10)

    assert [item['client_name'] for item in schedule] == ['ClientA']
    assert [client['client_name'] for client in unscheduled] == ['ClientB']


@patch("src.main.order_clients")
@patch("src.main.validate_addresses")
def test_build_schedule_skips_lunch_window(mock_validate, mock_order):
    mock_validate.return_value = []
    mock_order.return_value = [
        _client('ClientA', 'High', duration=180, travel_from_previous=0),
        _client('ClientB', 'Medium', duration=60, travel_from_previous=0),
    ]
    start = datetime(2030, 1, 1, 8, 0)

    schedule, unscheduled = build_schedule(DF, api_key="fake-key", start_date=start, end_hour=18)

    assert unscheduled == []
    assert schedule[1]['start_time'] == start.replace(hour=13, minute=0, second=0, microsecond=0)


@patch("src.main.order_clients")
@patch("src.main.validate_addresses")
def test_build_schedule_avoids_existing_appointments(mock_validate, mock_order):
    mock_validate.return_value = []
    mock_order.return_value = [_client('ClientA', 'High', duration=60, travel_from_previous=0)]
    start = datetime(2030, 1, 1, 8, 0)
    existing = [(datetime(2030, 1, 1, 9, 0), datetime(2030, 1, 1, 9, 30))]

    schedule, _ = build_schedule(
        DF, api_key="fake-key", start_date=start, existing_appointments=existing
    )

    assert schedule[0]['start_time'] == datetime(2030, 1, 1, 9, 30)


@patch("src.main.order_clients")
@patch("src.main.validate_addresses")
def test_build_schedule_uses_per_client_duration_column(mock_validate, mock_order):
    mock_validate.return_value = []
    mock_order.side_effect = lambda clients, origin, api_key: [
        {**c, 'distance_from_previous': '5 km', 'travel_minutes_from_previous': 0} for c in clients
    ]
    df = pd.DataFrame({
        'ClientName': ['Origin', 'ClientA', 'ClientB'],
        'Address': ['Start St', 'A St', 'B St'],
        'Priority': ['High', 'High', 'High'],
        'Duration': [None, 30, None],
    })
    start = datetime(2030, 1, 1, 8, 0)

    schedule, _ = build_schedule(df, api_key="fake-key", start_date=start, meeting_duration=60)

    assert schedule[0]['duration_minutes'] == 30  # from the Duration column
    assert schedule[1]['duration_minutes'] == 60  # falls back to the default


@patch("src.main.validate_addresses")
def test_build_schedule_raises_on_bad_addresses(mock_validate):
    mock_validate.return_value = ['A St']
    start = datetime(2030, 1, 1, 8, 0)

    with pytest.raises(AddressValidationError, match="A St"):
        build_schedule(DF, api_key="fake-key", start_date=start)


def test_parse_args_flags():
    args = parse_args(['--dry-run', '--date', '2030-01-01', '--duration', '30', '--file', 'x.xlsx'])
    assert args.dry_run is True
    assert args.date == '2030-01-01'
    assert args.duration == 30
    assert args.file == 'x.xlsx'
    assert args.set_priority is None


def test_parse_args_set_priority():
    args = parse_args(['--set-priority', 'Acme Co', 'High'])
    assert args.set_priority == ['Acme Co', 'High']


@patch("src.main.setup_logging")
@patch("src.main.save_excel")
@patch("src.main.add_priority")
@patch("src.main.read_excel")
@patch("src.main.load_config")
def test_main_set_priority_updates_and_saves(
    mock_load_config, mock_read_excel, mock_add_priority, mock_save_excel, mock_setup_logging
):
    mock_load_config.return_value = MagicMock(client_list_file='clients.xlsx')
    df = MagicMock()
    mock_read_excel.return_value = df

    main(['--set-priority', 'Acme Co', 'High'])

    mock_add_priority.assert_called_once_with(df, 'Acme Co', 'High')
    mock_save_excel.assert_called_once_with(df, 'clients.xlsx')


@patch("src.main.setup_logging")
@patch("src.main.schedule_appointment")
@patch("src.main.get_existing_appointments")
@patch("src.main.build_schedule")
@patch("src.main.read_excel")
@patch("src.main.load_config")
def test_main_dry_run_skips_outlook(
    mock_load_config, mock_read_excel, mock_build_schedule,
    mock_get_existing, mock_schedule_appointment, mock_setup_logging,
):
    mock_load_config.return_value = MagicMock(
        client_list_file='clients.xlsx', api_key='key', meeting_duration_minutes=60,
        start_hour=9, end_hour=17, lunch_start_hour=12, lunch_end_hour=13,
    )
    mock_read_excel.return_value = MagicMock()
    mock_build_schedule.return_value = ([{
        'client_name': 'A', 'priority': 'High', 'address': 'A St',
        'distance_from_previous': '5 km', 'travel_minutes_from_previous': 0,
        'start_time': datetime(2030, 1, 1, 9, 0), 'duration_minutes': 60,
    }], [])

    main(['--dry-run', '--date', '2030-01-01'])

    mock_get_existing.assert_not_called()
    mock_schedule_appointment.assert_not_called()
