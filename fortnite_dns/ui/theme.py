from tkinter import ttk

# ------------------------------------------------------------
# Palette (slate dark theme)
# ------------------------------------------------------------

BG = "#0b1120"
CARD = "#131c2e"
CARD2 = "#1e293b"
CARD3 = "#273449"
BORDER = "#24324a"
HOVER = "#334155"

TEXT = "#f1f5f9"
MUTED = "#94a3b8"
SUBTLE = "#64748b"

BLUE = "#3b82f6"
BLUE2 = "#2563eb"

PURPLE = "#8b5cf6"
PURPLE2 = "#7c3aed"

GREEN = "#22c55e"
GREEN2 = "#16a34a"

RED = "#ef4444"
RED2 = "#dc2626"

YELLOW = "#f59e0b"
YELLOW2 = "#d97706"
DARK_ON_YELLOW = "#1e1b09"

WHITE = "#ffffff"

ROW_ALT = "#172136"
SELECT = "#1d4ed8"
FAIL_FG = "#f87171"

# ------------------------------------------------------------
# Fonts
# ------------------------------------------------------------

FONT_FAMILY = "Segoe UI"

FONT_TITLE = (FONT_FAMILY, 20, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 10)
FONT_SECTION = (FONT_FAMILY, 9, "bold")
FONT_BODY = (FONT_FAMILY, 10)
FONT_BOLD = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 9)
FONT_TINY = (FONT_FAMILY, 8)
FONT_BEST = (FONT_FAMILY, 12, "bold")

# ------------------------------------------------------------
# Button variants: (bg, hover bg, fg)
# ------------------------------------------------------------

BUTTON_VARIANTS = {
    "neutral": (CARD3, HOVER, TEXT),
    "primary": (BLUE, BLUE2, WHITE),
    "purple": (PURPLE2, "#6d28d9", WHITE),
    "success": (GREEN2, "#15803d", WHITE),
    "danger": (RED2, "#b91c1c", WHITE),
    "warning": (YELLOW, YELLOW2, DARK_ON_YELLOW),
}


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
        bordercolor=BORDER,
        lightcolor=CARD,
        darkcolor=CARD,
        borderwidth=0,
        rowheight=34,
        font=FONT_BODY
    )

    style.layout(
        "Treeview",
        [("Treeview.treearea", {"sticky": "nswe"})]
    )

    style.configure(
        "Treeview.Heading",
        background=CARD2,
        foreground=MUTED,
        bordercolor=BORDER,
        lightcolor=CARD2,
        darkcolor=CARD2,
        relief="flat",
        padding=(6, 8),
        font=FONT_SECTION
    )

    style.map(
        "Treeview.Heading",
        background=[("active", CARD3)],
        foreground=[("active", TEXT)]
    )

    style.map(
        "Treeview",
        background=[("selected", SELECT)],
        foreground=[("selected", WHITE)]
    )

    style.configure(
        "TProgressbar",
        troughcolor=CARD2,
        background=BLUE,
        bordercolor=CARD2,
        lightcolor=BLUE,
        darkcolor=BLUE,
        borderwidth=0,
        thickness=6
    )

    style.configure(
        "TCombobox",
        fieldbackground=CARD2,
        background=CARD3,
        foreground=TEXT,
        arrowcolor=TEXT,
        bordercolor=BORDER,
        lightcolor=CARD2,
        darkcolor=CARD2,
        selectbackground=CARD2,
        selectforeground=TEXT,
        padding=(8, 5)
    )

    style.map(
        "TCombobox",
        fieldbackground=[("readonly", CARD2)],
        foreground=[("readonly", TEXT)],
        selectbackground=[("readonly", CARD2)],
        selectforeground=[("readonly", TEXT)],
        background=[("active", HOVER)]
    )

    for orient in ("Vertical", "Horizontal"):

        style.configure(
            f"{orient}.TScrollbar",
            background=CARD3,
            troughcolor=CARD,
            bordercolor=CARD,
            lightcolor=CARD3,
            darkcolor=CARD3,
            arrowcolor=MUTED,
            gripcount=0
        )

        style.map(
            f"{orient}.TScrollbar",
            background=[("active", HOVER)]
        )

    return style


def style_combobox_popup(root):
    """Dark colors for the Combobox dropdown list (a plain Listbox)."""

    root.option_add("*TCombobox*Listbox.background", CARD2)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", BLUE)
    root.option_add("*TCombobox*Listbox.selectForeground", WHITE)
    root.option_add("*TCombobox*Listbox.font", FONT_BODY)
