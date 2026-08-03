from datetime import datetime
from unittest.mock import patch

import pandas as pd

from src.main import build_schedule

DF = pd.DataFrame({
    'ClientName': ['Origin', 'LowPriorityClient', 'HighPriorityClient'],
    'Address': ['Start St', 'Low St', 'High St'],
    'Priority': ['Low', 'Low', 'High'],
})


@patch("src.main.get_distance_and_duration")
def test_build_schedule_orders_by_priority(mock_distance):
    mock_distance.return_value = ('5 km', 10)
    start = datetime(2030, 1, 1, 8, 0)

    schedule = build_schedule(DF, api_key="fake-key", start_date=start)

    assert [item['client_name'] for item in schedule] == ['HighPriorityClient', 'LowPriorityClient']
    assert schedule[0]['start_time'].hour == 9
    assert schedule[1]['start_time'] == schedule[0]['start_time'].replace() + \
        (schedule[1]['start_time'] - schedule[0]['start_time'])


@patch("src.main.get_distance_and_duration")
def test_build_schedule_spaces_appointments_by_duration_and_travel(mock_distance):
    mock_distance.return_value = ('5 km', 20)
    start = datetime(2030, 1, 1, 8, 0)

    schedule = build_schedule(DF, api_key="fake-key", start_date=start, meeting_duration=60)

    gap = schedule[1]['start_time'] - schedule[0]['start_time']
    assert gap.total_seconds() / 60 == 80  # 60 min meeting + 20 min travel
