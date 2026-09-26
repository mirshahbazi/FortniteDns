from tkinter import ttk

BG = "#0f172a"
CARD = "#1e293b"
CARD2 = "#334155"
TEXT = "#f8fafc"
MUTED = "#94a3b8"

BLUE = "#3b82f6"
BLUE2 = "#2563eb"

GREEN = "#22c55e"
GREEN2 = "#16a34a"

RED = "#ef4444"
RED2 = "#dc2626"

YELLOW = "#f59e0b"

WHITE = "#ffffff"


def configure_style():
    """
    Builds and returns a ttk.Style configured for the app's dark
    theme. Split out of App so the color palette can be reused or
    swapped without touching widget-construction code.
    """

    style = ttk.Style()

    try:
        style.theme_use("clam")
    except Exception:
        pass

    style.configure(
        "Treeview",
        background=CARD,
        foreground=TEXT,
        fieldbackground=CARD,
        borderwidth=0,
        rowheight=32,
        font=("Segoe UI", 10)
    )

    style.configure(
        "Treeview.Heading",
        background=CARD2,
        foreground=TEXT,
        font=("Segoe UI", 10, "bold")
    )

    style.map(
        "Treeview",
        background=[("selected", "#475569")],
        foreground=[("selected", WHITE)]
    )

    style.configure(
        "TProgressbar",
        troughcolor=CARD2,
        background=BLUE,
        borderwidth=0
    )

    return style
