import logging
import tkinter as tk

from src.gui.views.preview import PreviewView
from src.gui.views.progress import ProgressView
from src.gui.views.settings import SettingsView
from src.logging_setup import setup_logging

VIEW_CLASSES = (SettingsView, PreviewView, ProgressView)


class ClientMeetMaticApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ClientMeetMatic")
        self.geometry("760x520")
        self.minsize(640, 420)

        self.state = {
            'config': None,
            'df': None,
            'start_date': None,
            'schedule': None,
            'unscheduled': None,
        }

        container = tk.Frame(self)
        container.pack(fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.views = {}
        for view_class in VIEW_CLASSES:
            view = view_class(container, self)
            self.views[view_class.__name__] = view
            view.grid(row=0, column=0, sticky='nsew')

        self.show_view('SettingsView')

    def show_view(self, name):
        view = self.views[name]
        view.tkraise()
        if hasattr(view, 'on_show'):
            view.on_show()


def main():
    setup_logging(level=logging.INFO)
    app = ClientMeetMaticApp()
    app.mainloop()


if __name__ == "__main__":
    main()
