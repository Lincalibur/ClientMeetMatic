import win32com.client

def schedule_appointment(subject, start_time, duration, location, body):
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
