"""
Small reusable widgets for the responsive dark UI:

- FlowFrame: lays its children out left-to-right and wraps them
  onto new rows when the window gets narrow (like CSS flex-wrap).
- make_button: flat themed button with a hover effect.
- make_card: bordered card frame.
- make_entry: dark themed text entry with an optional placeholder.
"""

import tkinter as tk

from . import theme


class FlowFrame(tk.Frame):

    def __init__(self, master, hgap=8, vgap=8, **kwargs):

        super().__init__(master, **kwargs)

        self._items = []
        self._hgap = hgap
        self._vgap = vgap
        self._last_layout = None

        self.bind("<Configure>", self._on_configure)

    def add(self, widget, stretch=False):
        """
        Adds a child widget (it must have been created with this
        frame as its master). Stretch widgets expand to fill the
        rest of their row.
        """

        self._items.append((widget, stretch))
        self.after_idle(self._relayout)

        return widget

    def _on_configure(self, event):
        self._relayout(event.width)

    def _relayout(self, width=None):

        if not self.winfo_exists():
            return

        if width is None:
            width = self.winfo_width()

        if width <= 1:
            width = sum(w.winfo_reqwidth() + self._hgap for w, _ in self._items)

        rows = [[]]
        x = 0

        for widget, stretch in self._items:

            req = widget.winfo_reqwidth()

            if rows[-1] and x + req > width:
                rows.append([])
                x = 0

            rows[-1].append((widget, stretch, req))
            x += req + self._hgap

        layout = []
        y = 0

        for row in rows:

            if not row:
                continue

            height = max(w.winfo_reqheight() for w, _, _ in row)
            used = sum(req for _, _, req in row) + self._hgap * (len(row) - 1)
            extra = max(0, width - used)
            stretchers = [w for w, s, _ in row if s]
            bonus = extra // len(stretchers) if stretchers else 0

            x = 0

            for widget, stretch, req in row:

                w = req + (bonus if stretch else 0)
                layout.append((widget, x, y, w, height))
                x += w + self._hgap

            y += height + self._vgap

        total_height = max(1, y - self._vgap)

        signature = [(str(w), x, y, wd, h) for w, x, y, wd, h in layout]

        if signature == self._last_layout:
            return

        self._last_layout = signature

        for widget, x, y, w, h in layout:
            widget.place(x=x, y=y, width=w, height=h)

        self.configure(height=total_height)


def _hover(widget, normal_bg, hover_bg):

    def on_enter(_):
        if str(widget["state"]) != "disabled":
            widget.configure(bg=hover_bg)

    def on_leave(_):
        widget.configure(bg=normal_bg)

    widget.bind("<Enter>", on_enter, add="+")
    widget.bind("<Leave>", on_leave, add="+")


def make_button(master, text, command, variant="neutral", bold=True, **kwargs):

    bg, hover_bg, fg = theme.BUTTON_VARIANTS[variant]

    options = dict(
        text=text,
        command=command,
        bg=bg,
        fg=fg,
        activebackground=hover_bg,
        activeforeground=fg,
        disabledforeground=theme.SUBTLE if variant == "neutral" else "#cbd5e1",
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        font=theme.FONT_BOLD if bold else theme.FONT_BODY,
        padx=14,
        pady=7
    )

    options.update(kwargs)

    button = tk.Button(master, **options)

    _hover(button, bg, hover_bg)

    return button


def make_card(master, padx=16, pady=14, bg=None):

    return tk.Frame(
        master,
        bg=bg or theme.CARD,
        highlightbackground=theme.BORDER,
        highlightcolor=theme.BORDER,
        highlightthickness=1,
        padx=padx,
        pady=pady
    )


def make_section_label(master, text, bg=None):

    return tk.Label(
        master,
        text=text.upper() if text.isascii() else text,
        bg=bg or theme.CARD,
        fg=theme.SUBTLE,
        font=theme.FONT_SECTION
    )


def make_entry(master, textvariable, placeholder="", width=18):

    entry = tk.Entry(
        master,
        textvariable=textvariable,
        width=width,
        bg=theme.CARD2,
        fg=theme.TEXT,
        insertbackground=theme.TEXT,
        disabledbackground=theme.CARD2,
        relief="flat",
        highlightthickness=1,
        highlightbackground=theme.BORDER,
        highlightcolor=theme.BLUE,
        font=theme.FONT_BODY
    )

    if placeholder:
        _attach_placeholder(entry, textvariable, placeholder)

    return entry


def _attach_placeholder(entry, var, placeholder):
    """
    Shows grey hint text inside an empty entry. The hint is only
    drawn while the entry is unfocused and empty, and is never
    written into the StringVar, so callers read real values only.
    """

    hint = tk.Label(
        entry,
        text=placeholder,
        bg=theme.CARD2,
        fg=theme.SUBTLE,
        font=theme.FONT_SMALL,
        cursor="xterm"
    )

    def refresh(*_):

        if not entry.winfo_exists():
            return

        if var.get() or entry.focus_get() is entry:
            hint.place_forget()
        else:
            hint.place(x=4, rely=0.5, anchor="w")

    hint.bind("<Button-1>", lambda e: entry.focus_set())
    entry.bind("<FocusIn>", refresh, add="+")
    entry.bind("<FocusOut>", refresh, add="+")

    trace_id = var.trace_add("write", refresh)

    entry.bind(
        "<Destroy>",
        lambda e: _safe_trace_remove(var, trace_id),
        add="+"
    )

    entry.after_idle(refresh)


def _safe_trace_remove(var, trace_id):

    try:
        var.trace_remove("write", trace_id)
    except Exception:
        pass
