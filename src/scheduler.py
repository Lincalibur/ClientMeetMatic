from datetime import datetime, time as time_of_day

import pywintypes
import win32com.client

OL_FOLDER_CALENDAR = 9


class OutlookUnavailableError(RuntimeError):
    pass


def get_existing_appointments(date):
    """Returns [(start, end), ...] datetime tuples for every appointment already on the
    default Outlook calendar for the given date (recurring appointments included), used to
    avoid double-booking new appointments over existing ones."""
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        calendar = namespace.GetDefaultFolder(OL_FOLDER_CALENDAR)
        items = calendar.Items
        items.IncludeRecurrences = True
        items.Sort("[Start]")

        day_start = datetime.combine(date.date(), time_of_day.min)
        day_end = datetime.combine(date.date(), time_of_day.max)
        restriction = (
            f"[Start] < '{day_end:%m/%d/%Y %I:%M %p}' AND "
            f"[End] > '{day_start:%m/%d/%Y %I:%M %p}'"
        )
        restricted_items = items.Restrict(restriction)

        return [(item.Start, item.End) for item in restricted_items]
    except pywintypes.com_error as exc:
        raise OutlookUnavailableError(
            "Could not read the Outlook calendar. Make sure Microsoft Outlook is "
            "installed and configured on this machine."
        ) from exc


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
