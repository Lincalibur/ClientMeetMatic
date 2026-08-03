import pywintypes
import win32com.client


class OutlookUnavailableError(RuntimeError):
    pass


def schedule_appointment(subject, start_time, duration, location, body):
    """start_time may be a datetime or an Outlook-parseable string. duration is in minutes."""
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        appointment = outlook.CreateItem(1)  # 1: olAppointmentItem
        appointment.Subject = subject
        appointment.Start = start_time
        appointment.Duration = duration
        appointment.Location = location
        appointment.Body = body
        appointment.ReminderSet = True
        appointment.ReminderMinutesBeforeStart = 15
        appointment.Save()
        return appointment.EntryID
    except pywintypes.com_error as exc:
        raise OutlookUnavailableError(
            "Could not create the appointment in Outlook. Make sure Microsoft Outlook is "
            "installed and configured on this machine."
        ) from exc
