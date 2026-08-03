from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import pywintypes

from src.scheduler import OutlookUnavailableError, get_existing_appointments, schedule_appointment


@patch("src.scheduler.win32com.client.Dispatch")
def test_schedule_appointment_success(mock_dispatch):
    mock_appointment = MagicMock()
    mock_appointment.EntryID = "abc123"
    mock_dispatch.return_value.CreateItem.return_value = mock_appointment

    entry_id = schedule_appointment(
        subject="Meeting", start_time="2030-01-01 09:00", duration=60,
        location="Somewhere", body="Discuss things",
    )

    assert entry_id == "abc123"
    mock_appointment.Save.assert_called_once()
    assert mock_appointment.Subject == "Meeting"


@patch("src.scheduler.win32com.client.Dispatch")
def test_schedule_appointment_outlook_unavailable(mock_dispatch):
    mock_dispatch.side_effect = pywintypes.com_error(-2147221005, "Invalid class string", None, None)

    with pytest.raises(OutlookUnavailableError, match="Outlook"):
        schedule_appointment(
            subject="Meeting", start_time="2030-01-01 09:00", duration=60,
            location="Somewhere", body="Discuss things",
        )


@patch("src.scheduler.win32com.client.Dispatch")
def test_get_existing_appointments_returns_start_end_tuples(mock_dispatch):
    mock_item1 = MagicMock(Start=datetime(2030, 1, 1, 9, 0), End=datetime(2030, 1, 1, 9, 30))
    mock_item2 = MagicMock(Start=datetime(2030, 1, 1, 14, 0), End=datetime(2030, 1, 1, 14, 30))

    mock_items = MagicMock()
    mock_items.Restrict.return_value = [mock_item1, mock_item2]

    mock_calendar = MagicMock()
    mock_calendar.Items = mock_items

    mock_namespace = MagicMock()
    mock_namespace.GetDefaultFolder.return_value = mock_calendar
    mock_dispatch.return_value.GetNamespace.return_value = mock_namespace

    appointments = get_existing_appointments(datetime(2030, 1, 1))

    assert appointments == [
        (datetime(2030, 1, 1, 9, 0), datetime(2030, 1, 1, 9, 30)),
        (datetime(2030, 1, 1, 14, 0), datetime(2030, 1, 1, 14, 30)),
    ]
    mock_namespace.GetDefaultFolder.assert_called_once_with(9)


@patch("src.scheduler.win32com.client.Dispatch")
def test_get_existing_appointments_outlook_unavailable(mock_dispatch):
    mock_dispatch.side_effect = pywintypes.com_error(-2147221005, "Invalid class string", None, None)

    with pytest.raises(OutlookUnavailableError, match="Outlook"):
        get_existing_appointments(datetime(2030, 1, 1))
