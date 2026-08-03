import tkinter as tk

from src.config import AppConfig, load_config, save_config


class SettingsView(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(self, text="Settings", font=("Segoe UI", 16, "bold")).grid(
            row=0, column=0, columnspan=3, pady=(16, 12), padx=16, sticky='w'
        )

        self.api_key_var = tk.StringVar()
        self._row("Google Maps API key:", 1, tk.Entry(
            self, textvariable=self.api_key_var, show='*', width=44
        ))

        self.file_var = tk.StringVar()
        file_entry = tk.Entry(self, textvariable=self.file_var, width=36)
        file_entry.grid(row=2, column=1, sticky='we')
        tk.Label(self, text="Client list file:").grid(row=2, column=0, sticky='w', padx=16)
        tk.Button(self, text="Browse...", command=self._browse_file).grid(row=2, column=2, padx=(8, 16))

        self.start_hour_var = tk.IntVar()
        self._row("Business hours start (24h):", 3, tk.Spinbox(
            self, from_=0, to=23, textvariable=self.start_hour_var, width=5
        ))

        self.end_hour_var = tk.IntVar()
        self._row("Business hours end (24h):", 4, tk.Spinbox(
            self, from_=0, to=23, textvariable=self.end_hour_var, width=5
        ))

        self.lunch_start_var = tk.IntVar()
        self._row("Lunch start (24h):", 5, tk.Spinbox(
            self, from_=0, to=23, textvariable=self.lunch_start_var, width=5
        ))

        self.lunch_end_var = tk.IntVar()
        self._row("Lunch end (24h):", 6, tk.Spinbox(
            self, from_=0, to=23, textvariable=self.lunch_end_var, width=5
        ))

        self.duration_var = tk.IntVar()
        self._row("Default meeting duration (min):", 7, tk.Spinbox(
            self, from_=15, to=240, increment=15, textvariable=self.duration_var, width=5
        ))

        self.status_label = tk.Label(self, text="", fg="red", wraplength=560, justify='left')
        self.status_label.grid(row=8, column=0, columnspan=3, sticky='w', padx=16, pady=(8, 0))

        tk.Button(self, text="Save & Continue", command=self._save_and_continue).grid(
            row=9, column=0, columnspan=3, pady=16
        )

        self.grid_columnconfigure(1, weight=1)

    def _row(self, label, row, widget):
        tk.Label(self, text=label).grid(row=row, column=0, sticky='w', padx=16)
        widget.grid(row=row, column=1, sticky='w')

    def on_show(self):
        config = load_config()
        self.api_key_var.set(config.api_key or "")
        self.file_var.set(config.client_list_file)
        self.start_hour_var.set(config.start_hour)
        self.end_hour_var.set(config.end_hour)
        self.lunch_start_var.set(config.lunch_start_hour)
        self.lunch_end_var.set(config.lunch_end_hour)
        self.duration_var.set(config.meeting_duration_minutes)

    def _browse_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.file_var.set(path)

    def _save_and_continue(self):
        api_key = self.api_key_var.get().strip()
        if not api_key or api_key == 'YOUR_GOOGLE_MAPS_API_KEY':
            self.status_label.config(text="Enter a valid Google Maps API key.")
            return
        if not self.file_var.get().strip():
            self.status_label.config(text="Choose a client list file.")
            return
        if self.start_hour_var.get() >= self.end_hour_var.get():
            self.status_label.config(text="Business hours start must be before the end.")
            return
        if self.lunch_start_var.get() >= self.lunch_end_var.get():
            self.status_label.config(text="Lunch start must be before lunch end.")
            return

        config = AppConfig(
            api_key=api_key,
            client_list_file=self.file_var.get().strip(),
            meeting_duration_minutes=self.duration_var.get(),
            start_hour=self.start_hour_var.get(),
            end_hour=self.end_hour_var.get(),
            lunch_start_hour=self.lunch_start_var.get(),
            lunch_end_hour=self.lunch_end_var.get(),
        )
        save_config(config)
        self.status_label.config(text="")
        self.controller.state['config'] = config
        self.controller.show_view('PreviewView')
