import tkinter as tk

from src.config import get_app_data_dir
from src.scheduler import OutlookUnavailableError, schedule_appointment


class ProgressView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Booking Appointments", font=("Segoe UI", 16, "bold")).pack(
            padx=16, pady=(16, 8), anchor='w'
        )

        self.results = tk.Text(self, height=18, state='disabled', wrap='word')
        self.results.pack(fill='both', expand=True, padx=16)

        footer = tk.Frame(self)
        footer.pack(fill='x', padx=16, pady=16)
        self.log_label = tk.Label(footer, text="")
        self.log_label.pack(side='left')
        tk.Button(
            footer, text="Back to Preview", command=lambda: controller.show_view('PreviewView')
        ).pack(side='right')

    def on_show(self):
        self.log_label.config(text=f"Log file: {get_app_data_dir() / 'logs' / 'app.log'}")
        self._book_all()

    def _log(self, message):
        self.results.config(state='normal')
        self.results.insert('end', message + "\n")
        self.results.see('end')
        self.results.config(state='disabled')
        self.update_idletasks()

    def _book_all(self):
        self.results.config(state='normal')
        self.results.delete('1.0', 'end')
        self.results.config(state='disabled')

        schedule = self.controller.state.get('schedule') or []
        if not schedule:
            self._log("Nothing to book — run a preview first.")
            return

        for item in schedule:
            try:
                schedule_appointment(
                    subject=f"Meeting with {item['client_name']}",
                    start_time=item['start_time'],
                    duration=item['duration_minutes'],
                    location=item['address'],
                    body=f"Discuss with {item['client_name']} (Priority: {item['priority']})",
                )
                self._log(f"Booked {item['client_name']} at {item['start_time']:%Y-%m-%d %H:%M}")
            except OutlookUnavailableError as exc:
                self._log(f"FAILED: {item['client_name']} - {exc}")

        unscheduled = self.controller.state.get('unscheduled') or []
        if unscheduled:
            self._log("")
            self._log("Could not fit into today's schedule:")
            for client in unscheduled:
                self._log(f"  {client['client_name']} ({client['priority']})")
