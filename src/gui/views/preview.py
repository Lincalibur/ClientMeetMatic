import tkinter as tk
from datetime import datetime, timedelta
from tkinter import ttk

from src.distance_calculator import DistanceLookupError
from src.excel_handler import VALID_PRIORITIES, add_priority, read_excel, save_excel
from src.geocoder import AddressValidationError
from src.main import build_schedule
from src.scheduler import OutlookUnavailableError, get_existing_appointments

COLUMNS = ('priority', 'address', 'distance', 'travel', 'start', 'duration')


class PreviewView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.df = None

        header = tk.Frame(self)
        header.pack(fill='x', padx=16, pady=(16, 8))
        tk.Label(header, text="Route Preview", font=("Segoe UI", 16, "bold")).pack(side='left')
        tk.Button(header, text="Refresh", command=self._run_preview).pack(side='right')
        tk.Button(
            header, text="Back to Settings", command=lambda: controller.show_view('SettingsView')
        ).pack(side='right', padx=(0, 8))

        self.tree = ttk.Treeview(self, columns=COLUMNS, show='tree headings', height=12)
        self.tree.heading('#0', text='Client')
        self.tree.heading('priority', text='Priority')
        self.tree.heading('address', text='Address')
        self.tree.heading('distance', text='Distance')
        self.tree.heading('travel', text='Travel (min)')
        self.tree.heading('start', text='Start Time')
        self.tree.heading('duration', text='Duration (min)')
        self.tree.pack(fill='both', expand=True, padx=16)
        self.tree.bind('<Double-1>', self._cycle_priority)

        self.unscheduled_label = tk.Label(self, text="", fg="darkorange", wraplength=680, justify='left')
        self.unscheduled_label.pack(fill='x', padx=16, anchor='w')

        self.status_label = tk.Label(self, text="", fg="red", wraplength=680, justify='left')
        self.status_label.pack(fill='x', padx=16, anchor='w')

        footer = tk.Frame(self)
        footer.pack(fill='x', padx=16, pady=16)
        tk.Label(footer, text="Double-click a row to cycle its priority.").pack(side='left')
        self.book_button = tk.Button(footer, text="Book It", state='disabled', command=self._go_to_progress)
        self.book_button.pack(side='right')

    def on_show(self):
        self._run_preview()

    def _run_preview(self):
        config = self.controller.state['config']
        if config is None:
            self.status_label.config(text="Save your settings first.")
            self.tree.delete(*self.tree.get_children())
            self.unscheduled_label.config(text="")
            return

        self.status_label.config(text="Loading...")
        self.book_button.config(state='disabled')
        self.update_idletasks()

        try:
            self.df = read_excel(config.client_list_file)
            start_date = datetime.now() + timedelta(days=1)
            try:
                existing_appointments = get_existing_appointments(start_date)
            except OutlookUnavailableError:
                existing_appointments = []

            schedule, unscheduled = build_schedule(
                self.df,
                config.api_key,
                start_date,
                meeting_duration=config.meeting_duration_minutes,
                start_hour=config.start_hour,
                end_hour=config.end_hour,
                lunch_start_hour=config.lunch_start_hour,
                lunch_end_hour=config.lunch_end_hour,
                existing_appointments=existing_appointments,
            )
        except (DistanceLookupError, AddressValidationError, ValueError) as exc:
            self.status_label.config(text=str(exc))
            self.tree.delete(*self.tree.get_children())
            self.unscheduled_label.config(text="")
            return

        self.controller.state['start_date'] = start_date
        self.controller.state['schedule'] = schedule
        self.controller.state['unscheduled'] = unscheduled

        self.tree.delete(*self.tree.get_children())
        for item in schedule:
            self.tree.insert('', 'end', iid=item['client_name'], text=item['client_name'], values=(
                item['priority'],
                item['address'],
                item['distance_from_previous'],
                item['travel_minutes_from_previous'],
                item['start_time'].strftime('%Y-%m-%d %H:%M'),
                item['duration_minutes'],
            ))

        self.status_label.config(text="")
        if unscheduled:
            names = ", ".join(client['client_name'] for client in unscheduled)
            self.unscheduled_label.config(text=f"Didn't fit into today's business hours: {names}")
        else:
            self.unscheduled_label.config(text="")

        self.book_button.config(state='normal' if schedule else 'disabled')

    def _cycle_priority(self, event):
        item_id = self.tree.identify_row(event.y)
        if not item_id or self.df is None:
            return

        config = self.controller.state['config']
        options = sorted(VALID_PRIORITIES, key=lambda p: ('High', 'Medium', 'Low').index(p))
        current_priority = self.tree.set(item_id, 'priority')
        next_priority = options[(options.index(current_priority) + 1) % len(options)]

        add_priority(self.df, item_id, next_priority)
        save_excel(self.df, config.client_list_file)
        self._run_preview()

    def _go_to_progress(self):
        self.controller.show_view('ProgressView')
