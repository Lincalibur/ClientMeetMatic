from unittest.mock import MagicMock, patch

import pytest
import pywintypes

from src.scheduler import OutlookUnavailableError, schedule_appointment


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
