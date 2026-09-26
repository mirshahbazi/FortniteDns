import tkinter as tk
from tkinter import messagebox

from .resolver import DnsResolver
from .ui.app import App
from .utils import is_admin, relaunch_as_admin


def main():

    # Get elevation up front, before any window opens. Elevating
    # later (when the user clicks Apply) meant closing and
    # reopening the whole app mid-session, which is jarring even
    # though the pending choice now survives the restart. If the
    # user declines the UAC prompt here, fall back to running
    # unelevated — Apply will still offer to elevate at that point.
    if not is_admin():

        if relaunch_as_admin():
            return

    if not DnsResolver.is_available():

        root = tk.Tk()
        root.withdraw()

        messagebox.showerror(
            "Missing dependency",
            (
                "dnspython is required.\n\n"
                "Run:\n\n"
                "py -m pip install dnspython"
            )
        )

        return

    root = tk.Tk()

    App(root)

    root.mainloop()
