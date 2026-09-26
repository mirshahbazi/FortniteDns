import statistics
import threading
import tkinter as tk
import webbrowser
from tkinter import messagebox, ttk

from .. import VERSION
from ..config_store import ConfigStore
from ..constants import (
    AUTHOR_EMAIL,
    AUTHOR_LINK,
    AUTHOR_NAME,
    BUILTIN_DNS,
    DEFAULT_FALLBACK_SECONDARY,
    DONATE_URL,
)
from ..dns_sources import DnsSourceProvider
from ..i18n import DEFAULT_LANGUAGE, Translator
from ..network import WindowsNetworkManager
from ..pinger import WindowsPinger
from ..resolver import DnsResolver
from ..sound import play_sound
from ..tcp_pinger import TcpPinger
from ..testers import FastDnsTester, FortniteDnsTester
from ..tracer import RouteTracer
from ..utils import is_admin, is_ipv4, relaunch_as_admin
from . import theme


class App:

    def __init__(
        self,
        root,
        config_store=None,
        network=None,
        dns_sources=None,
        fast_tester=None,
        fortnite_tester=None,
        tcp_pinger=None,
        route_tracer=None,
        language=None
    ):

        self.root = root

        # Collaborators are constructor-injectable (with sensible
        # real-world defaults) so the app can be driven in tests
        # with fakes, without needing Tkinter or a real network.
        self.config_store = config_store or ConfigStore()
        self.network = network or WindowsNetworkManager()
        self.dns_sources = dns_sources or DnsSourceProvider()
        self.tcp_pinger = tcp_pinger or TcpPinger()
        self.route_tracer = route_tracer or RouteTracer()

        resolver = DnsResolver()
        pinger = WindowsPinger()

        self.fast_tester = fast_tester or FastDnsTester(resolver)
        self.fortnite_tester = fortnite_tester or FortniteDnsTester(resolver, pinger)

        self.i18n = Translator(language or DEFAULT_LANGUAGE)

        self.dns_list = []
        self.results = []
        self.best_result = None
        self.table_mode = "simple"

        self.testing = False
        self.cancel_requested = False

        self.online_dns = []
        self.custom_dns = self.config_store.get_custom_dns()

        self.root.geometry("1250x820")
        self.root.minsize(1050, 720)
        self.root.configure(bg=theme.BG)

        self.build_style()
        self.build_ui()

        self.load_adapters()

        # Load built-in + saved custom DNS immediately.
        self.rebuild_dns_list()

        # Automatically fetch online list.
        threading.Thread(
            target=self.load_online_list,
            daemon=True
        ).start()

        # If a previous run had to elevate to Administrator to
        # apply a DNS choice, finish that job now instead of
        # making the user redo the whole test.
        self.root.after(
            200,
            self.check_pending_apply
        )

    def t(self, key, **kwargs):
        return self.i18n.t(key, **kwargs)

    # ========================================================
    # STYLE
    # ========================================================

    def build_style(self):
        theme.configure_style()

    # ========================================================
    # LANGUAGE
    # ========================================================

    def toggle_language(self):

        self.i18n.set_language(self.i18n.other_language())

        selected_adapter = self.adapter_var.get()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.build_ui()

        self.load_adapters()

        if selected_adapter:
            self.adapter_var.set(selected_adapter)
            self.update_current_dns()

        if self.table_mode == "results":
            self.refresh_table()
        else:
            self.refresh_table(simple=True)

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        self.root.title(f"{self.t('app.title')} {VERSION}")

        # HEADER
        header = tk.Frame(self.root, bg=theme.BG)

        header.pack(
            fill="x",
            padx=25,
            pady=(20, 10)
        )

        header_left = tk.Frame(header, bg=theme.BG)
        header_left.pack(side="left", fill="x", expand=True)

        header_right = tk.Frame(header, bg=theme.BG)
        header_right.pack(side="right")

        tk.Label(
            header_left,
            text=f"🎮 {self.t('app.title')}",
            bg=theme.BG,
            fg=theme.TEXT,
            font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")

        tk.Label(
            header_left,
            text=self.t("app.subtitle"),
            bg=theme.BG,
            fg=theme.MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(3, 0))

        tk.Button(
            header_right,
            text=self.t("button.language"),
            command=self.toggle_language,
            bg=theme.CARD2,
            fg=theme.TEXT,
            activebackground="#475569",
            activeforeground=theme.TEXT,
            relief="flat",
            padx=10,
            pady=6
        ).pack(side="right", padx=(6, 0))

        tk.Button(
            header_right,
            text=self.t("button.about"),
            command=self.show_about,
            bg=theme.CARD2,
            fg=theme.TEXT,
            activebackground="#475569",
            activeforeground=theme.TEXT,
            relief="flat",
            padx=10,
            pady=6
        ).pack(side="right")

        # CONTROL BAR
        control = tk.Frame(
            self.root,
            bg=theme.CARD,
            padx=15,
            pady=13
        )

        control.pack(fill="x", padx=25, pady=8)

        tk.Label(
            control,
            text=self.t("label.adapter"),
            bg=theme.CARD,
            fg=theme.TEXT
        ).grid(row=0, column=0, padx=(0, 5))

        self.adapter_var = tk.StringVar()

        self.adapter_combo = ttk.Combobox(
            control,
            textvariable=self.adapter_var,
            state="readonly",
            width=25
        )

        self.adapter_combo.grid(row=0, column=1, padx=5)

        tk.Button(
            control,
            text="↻",
            command=self.load_adapters,
            bg=theme.CARD2,
            fg=theme.TEXT,
            activebackground="#475569",
            activeforeground=theme.TEXT,
            relief="flat",
            width=4
        ).grid(row=0, column=2, padx=4)

        self.online_button = tk.Button(
            control,
            text=self.t("button.update_dns_list"),
            command=self.update_online_clicked,
            bg=theme.CARD2,
            fg=theme.TEXT,
            activebackground="#475569",
            activeforeground=theme.TEXT,
            relief="flat",
            padx=12,
            pady=7
        )

        self.online_button.grid(row=0, column=3, padx=(20, 5))

        self.fast_button = tk.Button(
            control,
            text=self.t("button.fast_test"),
            command=self.start_fast_test,
            bg=theme.BLUE,
            fg=theme.WHITE,
            activebackground=theme.BLUE2,
            activeforeground=theme.WHITE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=8
        )

        self.fast_button.grid(row=0, column=4, padx=5)

        self.fortnite_button = tk.Button(
            control,
            text=self.t("button.fortnite_test"),
            command=self.start_fortnite_test,
            bg="#7c3aed",
            fg=theme.WHITE,
            activebackground="#6d28d9",
            activeforeground=theme.WHITE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=8
        )

        self.fortnite_button.grid(row=0, column=5, padx=5)

        self.apply_button = tk.Button(
            control,
            text=self.t("button.apply_best"),
            command=self.apply_best,
            bg=theme.GREEN,
            fg=theme.WHITE,
            activebackground=theme.GREEN2,
            activeforeground=theme.WHITE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8,
            state="disabled"
        )

        self.apply_button.grid(row=0, column=6, padx=5)

        self.clear_button = tk.Button(
            control,
            text=self.t("button.clear_dns"),
            command=self.clear_dns,
            bg=theme.RED,
            fg=theme.WHITE,
            activebackground=theme.RED2,
            activeforeground=theme.WHITE,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=13,
            pady=8
        )

        self.clear_button.grid(row=0, column=7, padx=5)

        self.cancel_button = tk.Button(
            control,
            text=self.t("button.cancel"),
            command=self.cancel_test,
            bg=theme.CARD2,
            fg=theme.TEXT,
            activebackground="#475569",
            activeforeground=theme.TEXT,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=13,
            pady=8,
            state="disabled"
        )

        self.cancel_button.grid(row=0, column=8, padx=5)

        self.reality_button = tk.Button(
            control,
            text=self.t("button.reality_check"),
            command=self.start_reality_check,
            bg=theme.YELLOW,
            fg="#1e1b09",
            activebackground="#d97706",
            activeforeground="#1e1b09",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=13,
            pady=8
        )

        self.reality_button.grid(row=0, column=9, padx=5)

        self.route_button = tk.Button(
            control,
            text=self.t("button.route_check"),
            command=self.start_route_check,
            bg=theme.CARD2,
            fg=theme.TEXT,
            activebackground="#475569",
            activeforeground=theme.TEXT,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            padx=13,
            pady=8
        )

        self.route_button.grid(row=0, column=10, padx=5)

        # MANUAL DNS ENTRY
        manual = tk.Frame(
            self.root,
            bg=theme.CARD,
            padx=15,
            pady=10
        )

        manual.pack(fill="x", padx=25, pady=(0, 8))

        tk.Label(
            manual,
            text=self.t("label.add_manual_dns"),
            bg=theme.CARD,
            fg=theme.TEXT
        ).grid(row=0, column=0, padx=(0, 8))

        self.custom_name_var = tk.StringVar()
        self.custom_primary_var = tk.StringVar()
        self.custom_secondary_var = tk.StringVar()

        tk.Entry(
            manual,
            textvariable=self.custom_name_var,
            width=16
        ).grid(row=0, column=1, padx=4)

        tk.Entry(
            manual,
            textvariable=self.custom_primary_var,
            width=16
        ).grid(row=0, column=2, padx=4)

        tk.Entry(
            manual,
            textvariable=self.custom_secondary_var,
            width=16
        ).grid(row=0, column=3, padx=4)

        tk.Label(
            manual,
            text=self.t("label.manual_hint"),
            bg=theme.CARD,
            fg=theme.MUTED,
            font=("Segoe UI", 8)
        ).grid(row=0, column=4, padx=8)

        tk.Button(
            manual,
            text=self.t("button.add"),
            command=self.add_custom_dns,
            bg=theme.BLUE,
            fg=theme.WHITE,
            activebackground=theme.BLUE2,
            activeforeground=theme.WHITE,
            relief="flat",
            padx=12,
            pady=4
        ).grid(row=0, column=5, padx=(8, 0))

        # Progress
        progress_frame = tk.Frame(self.root, bg=theme.BG)

        progress_frame.pack(fill="x", padx=25, pady=5)

        self.progress = ttk.Progressbar(
            progress_frame,
            mode="determinate"
        )

        self.progress.pack(fill="x")

        self.status_var = tk.StringVar(
            value=self.t("status.loading")
        )

        tk.Label(
            progress_frame,
            textvariable=self.status_var,
            bg=theme.BG,
            fg=theme.MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(4, 0))

        # Current DNS
        current_frame = tk.Frame(self.root, bg=theme.CARD)

        current_frame.pack(fill="x", padx=25, pady=7)

        self.current_dns_var = tk.StringVar(value="...")

        tk.Label(
            current_frame,
            textvariable=self.current_dns_var,
            bg=theme.CARD,
            fg=theme.TEXT,
            font=("Segoe UI", 10, "bold"),
            padx=12,
            pady=8
        ).pack(anchor="w")

        self.adapter_combo.bind(
            "<<ComboboxSelected>>",
            lambda e: self.update_current_dns()
        )

        # TABLE
        table_frame = tk.Frame(self.root, bg=theme.BG)

        table_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=8
        )

        columns = (
            "name", "dns", "fast", "success",
            "bahrain", "mumbai", "israel", "germany", "uk",
            "score", "status"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "name": self.t("table.col.name"),
            "dns": self.t("table.col.dns"),
            "fast": self.t("table.col.fast"),
            "success": self.t("table.col.success"),
            "bahrain": self.t("table.col.bahrain"),
            "mumbai": self.t("table.col.mumbai"),
            "israel": self.t("table.col.israel"),
            "germany": self.t("table.col.germany"),
            "uk": self.t("table.col.uk"),
            "score": self.t("table.col.score"),
            "status": self.t("table.col.status"),
        }

        widths = {
            "name": 140, "dns": 115, "fast": 90, "success": 75,
            "bahrain": 90, "mumbai": 90, "israel": 90, "germany": 90,
            "uk": 90, "score": 80, "status": 100
        }

        for col in columns:

            self.tree.heading(col, text=headings[col])

            self.tree.column(
                col,
                width=widths[col],
                anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.apply_selected)
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Bottom
        bottom = tk.Frame(
            self.root,
            bg=theme.CARD,
            padx=15,
            pady=12
        )

        bottom.pack(fill="x", padx=25, pady=(5, 20))

        self.best_var = tk.StringVar(
            value=self.t("best.initial")
        )

        tk.Label(
            bottom,
            textvariable=self.best_var,
            bg=theme.CARD,
            fg=theme.GREEN,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w")

        self.info_var = tk.StringVar(
            value=self.t("info.default")
        )

        tk.Label(
            bottom,
            textvariable=self.info_var,
            bg=theme.CARD,
            fg=theme.MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            self.root,
            text=self.t("footer.disclaimer"),
            bg=theme.BG,
            fg="#64748b",
            font=("Segoe UI", 8)
        ).pack(pady=(0, 10))

    # ========================================================
    # ABOUT
    # ========================================================

    def show_about(self):

        win = tk.Toplevel(self.root)
        win.title(self.t("about.title"))
        win.configure(bg=theme.CARD)
        win.resizable(False, False)
        win.transient(self.root)

        tk.Label(
            win,
            text=self.t("app.title"),
            bg=theme.CARD,
            fg=theme.TEXT,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(18, 4), padx=30)

        tk.Label(
            win,
            text=f"{self.t('about.version')}: {VERSION}",
            bg=theme.CARD,
            fg=theme.MUTED
        ).pack()

        tk.Label(
            win,
            text=f"{self.t('about.author')}: {AUTHOR_NAME}",
            bg=theme.CARD,
            fg=theme.TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(16, 2))

        if AUTHOR_EMAIL:

            tk.Label(
                win,
                text=AUTHOR_EMAIL,
                bg=theme.CARD,
                fg=theme.MUTED
            ).pack()

        if AUTHOR_LINK:

            link = tk.Label(
                win,
                text=AUTHOR_LINK,
                bg=theme.CARD,
                fg=theme.BLUE,
                cursor="hand2"
            )

            link.pack(pady=(4, 0))

            link.bind(
                "<Button-1>",
                lambda e: webbrowser.open(AUTHOR_LINK)
            )

        tk.Label(
            win,
            text=self.t("about.donate_title"),
            bg=theme.CARD,
            fg=theme.TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(pady=(18, 2))

        if DONATE_URL:

            donate_link = tk.Label(
                win,
                text=self.t("about.donate_link_text"),
                bg=theme.CARD,
                fg=theme.GREEN,
                cursor="hand2"
            )

            donate_link.pack()

            donate_link.bind(
                "<Button-1>",
                lambda e: webbrowser.open(DONATE_URL)
            )

        else:

            tk.Label(
                win,
                text=self.t("about.donate_coming_soon"),
                bg=theme.CARD,
                fg=theme.MUTED
            ).pack()

        tk.Button(
            win,
            text=self.t("common.close"),
            command=win.destroy,
            bg=theme.CARD2,
            fg=theme.TEXT,
            activebackground="#475569",
            activeforeground=theme.TEXT,
            relief="flat",
            padx=15,
            pady=6
        ).pack(pady=18)

    # ========================================================
    # PENDING APPLY (post-elevation resume)
    # ========================================================

    def check_pending_apply(self):

        pending = self.config_store.pop_pending_apply()

        if pending is None:
            return

        if not is_admin():
            return

        adapter = pending.get("adapter")
        item = pending.get("item")

        if not adapter or not item or not item.get("primary"):
            return

        available = self.adapter_combo["values"] or []

        if adapter in available:
            self.adapter_var.set(adapter)

        success, message = self.network.set_dns(
            adapter,
            item["primary"],
            item.get("secondary", "")
        )

        if success:

            self.update_current_dns()

            play_sound("success")

            messagebox.showinfo(
                self.t("msgbox.dns_applied_title"),
                self.t(
                    "msgbox.dns_applied_auto",
                    name=item["name"],
                    primary=item["primary"],
                    secondary=item.get("secondary") or self.t("msgbox.na"),
                    adapter=adapter
                )
            )

        else:

            play_sound("error")

            messagebox.showerror(
                self.t("msgbox.dns_error_title"),
                message
            )

    # ========================================================
    # ADAPTER
    # ========================================================

    def load_adapters(self):

        adapters = self.network.get_active_adapters()

        self.adapter_combo["values"] = adapters

        if not adapters:

            self.adapter_var.set("")

            self.current_dns_var.set(
                self.t("status.current_dns_prefix")
                + self.t("status.current_dns_none")
            )

            return

        current = self.adapter_var.get()

        if current in adapters:
            selected = current

        else:

            selected = adapters[0]

            for adapter in adapters:

                low = adapter.lower()

                if (
                    "wi-fi" in low
                    or "wifi" in low
                    or "ethernet" in low
                ):

                    selected = adapter
                    break

        self.adapter_var.set(selected)

        self.update_current_dns()

    def update_current_dns(self):

        adapter = self.adapter_var.get()

        if not adapter:
            return

        dns_list = self.network.get_current_dns(adapter)

        prefix = self.t("status.current_dns_prefix")

        if dns_list:
            self.current_dns_var.set(prefix + "  |  ".join(dns_list))
        else:
            self.current_dns_var.set(prefix + self.t("status.current_dns_dhcp"))

    # ========================================================
    # DNS LIST
    # ========================================================

    def rebuild_dns_list(self):

        self.dns_list = self.dns_sources.merge(
            BUILTIN_DNS,
            self.online_dns,
            self.custom_dns
        )

        self.refresh_table(simple=True)

        self.status_var.set(
            self.t("status.loaded_count", count=len(self.dns_list))
        )

    def load_online_list(self):

        online = self.dns_sources.fetch_online()

        self.root.after(
            0,
            lambda: self.finish_online_load(online)
        )

    def finish_online_load(self, online):

        self.online_dns = online

        self.rebuild_dns_list()

        self.status_var.set(
            self.t(
                "status.loaded_with_online",
                count=len(self.dns_list),
                online=len(online)
            )
        )

        play_sound("success")

    def update_online_clicked(self):

        if self.testing:
            return

        self.online_button.config(
            state="disabled",
            text=self.t("button.updating")
        )

        self.status_var.set(self.t("status.downloading_online"))

        threading.Thread(
            target=self.update_online_worker,
            daemon=True
        ).start()

    def update_online_worker(self):

        online = self.dns_sources.fetch_online()

        self.root.after(
            0,
            lambda: self.finish_manual_update(online)
        )

    def finish_manual_update(self, online):

        self.online_button.config(
            state="normal",
            text=self.t("button.update_dns_list")
        )

        if not online:

            self.status_var.set(self.t("status.online_unavailable"))

            play_sound("warning")

            return

        self.online_dns = online

        self.rebuild_dns_list()

        self.status_var.set(
            self.t("status.updated_count", count=len(self.dns_list))
        )

        play_sound("success")

    # ========================================================
    # CUSTOM DNS (manual entry)
    # ========================================================

    def add_custom_dns(self):

        if self.testing:
            return

        name = (
            self.custom_name_var.get().strip()
            or "Custom DNS"
        )

        primary = self.custom_primary_var.get().strip()
        secondary = self.custom_secondary_var.get().strip()

        if not is_ipv4(primary):

            messagebox.showwarning(
                self.t("msgbox.custom_dns_title"),
                self.t("msgbox.invalid_primary")
            )

            return

        if secondary and not is_ipv4(secondary):

            messagebox.showwarning(
                self.t("msgbox.custom_dns_title"),
                self.t("msgbox.invalid_secondary")
            )

            return

        self.custom_dns.append((name, primary, secondary))

        self.config_store.set_custom_dns(self.custom_dns)

        self.rebuild_dns_list()

        self.custom_name_var.set("")
        self.custom_primary_var.set("")
        self.custom_secondary_var.set("")

        self.status_var.set(
            self.t(
                "status.added_custom",
                name=name,
                count=len(self.dns_list)
            )
        )

    # ========================================================
    # TABLE
    # ========================================================

    def refresh_table(self, simple=False):

        self.table_mode = "simple" if simple else "results"

        self.tree.delete(*self.tree.get_children())

        if simple:

            ready_text = self.t("table.status.ready")

            for item in self.dns_list:

                self.tree.insert(
                    "",
                    "end",
                    values=(
                        item[0], item[1],
                        "-", "-", "-", "-", "-", "-", "-", "-",
                        ready_text
                    )
                )

            return

        for item in self.results:
            self.insert_result(item)

    def get_row_record(self, index):
        """
        Normalizes whichever data source currently backs the table
        (raw dns_list tuples before any test, or result dicts after
        one) into a plain {name, primary, secondary} dict, so the
        right-click menu can work regardless of test state.
        """

        if self.table_mode == "results":

            if index < 0 or index >= len(self.results):
                return None

            item = self.results[index]

            return {
                "name": item["name"],
                "primary": item["primary"],
                "secondary": item.get("secondary", "")
            }

        if index < 0 or index >= len(self.dns_list):
            return None

        name, primary, secondary = self.dns_list[index]

        return {
            "name": name,
            "primary": primary,
            "secondary": secondary
        }

    def insert_result(self, item):

        fast = item.get("avg")
        success = item.get("success", 0)

        fortnite = {
            x["region"]: x
            for x in item.get("fortnite", [])
        }

        fail_text = self.t("table.fail")

        def ping(region):

            r = fortnite.get(region)

            if not r:
                return "-"

            if r["avg"] is None:
                return fail_text

            return f"{r['avg']:.0f} ms"

        fast_text = fail_text if fast is None else f"{fast:.1f} ms"

        score = item.get("score")

        score_text = (
            f"{score:.1f}"
            if score is not None and score != float("inf")
            else "-"
        )

        self.tree.insert(
            "",
            "end",
            values=(
                item["name"],
                item["primary"],
                fast_text,
                f"{success:.0f}%",
                ping("Bahrain"),
                ping("Mumbai"),
                ping("Israel"),
                ping("Germany"),
                ping("United Kingdom"),
                score_text,
                self.t("table.status.ok")
            )
        )

    # ========================================================
    # CONTEXT MENU (primary / secondary)
    # ========================================================

    def show_context_menu(self, event):

        row_id = self.tree.identify_row(event.y)

        if not row_id:
            return

        self.tree.selection_set(row_id)

        index = self.tree.index(row_id)

        record = self.get_row_record(index)

        if not record:
            return

        menu = tk.Menu(self.root, tearoff=0)

        menu.add_command(
            label=self.t("menu.apply_both"),
            command=lambda: self.apply_dns_item(self.ensure_secondary(record))
        )

        menu.add_command(
            label=self.t("menu.set_primary"),
            command=lambda: self.apply_role(record, "primary")
        )

        menu.add_command(
            label=self.t("menu.set_secondary"),
            command=lambda: self.apply_role(record, "secondary")
        )

        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def apply_role(self, record, role):
        """
        Sets just one slot (primary or secondary) on the adapter,
        keeping whatever is already in the other slot — e.g. keep
        your current primary and only swap the secondary for a
        candidate from the list.
        """

        adapter = self.adapter_var.get()

        if not adapter:

            messagebox.showwarning(
                self.t("msgbox.adapter_title"),
                self.t("msgbox.select_adapter")
            )

            return

        current = self.network.get_current_dns(adapter)

        current_primary = current[0] if len(current) > 0 else ""
        current_secondary = current[1] if len(current) > 1 else ""

        if role == "primary":

            new_primary = record["primary"]
            new_secondary = current_secondary

        else:

            if not current_primary:

                messagebox.showwarning(
                    self.t("msgbox.dns_title"),
                    self.t("msgbox.set_primary_first")
                )

                return

            new_primary = current_primary
            new_secondary = record["primary"]

        role_label = self.t(
            "menu.set_primary" if role == "primary" else "menu.set_secondary"
        )

        synthetic_item = {
            "name": f"{record['name']} — {role_label}",
            "primary": new_primary,
            "secondary": new_secondary
        }

        # Deliberately NOT run through ensure_secondary: the whole
        # point of "primary/secondary only" is to touch just one
        # slot and leave whatever's already in the other one alone,
        # even if that's empty.
        self.apply_dns_item(synthetic_item)

    def ensure_secondary(self, item):
        """
        Fills in a missing secondary before an "apply both" action,
        so the adapter never ends up with only one DNS server (no
        failover) just because the winning candidate happened to be
        a scraped online entry or a manually-added one left blank —
        DNS Jumper always ships its providers as pairs, this is the
        equivalent for candidates that don't have a pair of their
        own. Prefers the next different candidate from the most
        recent test results (still an empirically decent resolver);
        falls back to a fixed, always-available default.
        """

        if item.get("secondary"):
            return item

        fallback = None

        for other in self.results:

            other_primary = other.get("primary")

            if (
                other_primary
                and other_primary != item["primary"]
                and is_ipv4(other_primary)
            ):
                fallback = other_primary
                break

        if not fallback:
            fallback = DEFAULT_FALLBACK_SECONDARY

        return {**item, "secondary": fallback}

    # ========================================================
    # FAST TEST
    # ========================================================

    def start_fast_test(self):

        if self.testing:
            return

        if not self.dns_list:

            messagebox.showwarning(
                self.t("msgbox.dns_title"),
                self.t("msgbox.no_dns_loaded")
            )

            return

        self.testing = True
        self.cancel_requested = False

        self.disable_buttons()

        self.results = []
        self.best_result = None

        self.progress["value"] = 0

        self.status_var.set(
            self.t("status.fast_testing", count=len(self.dns_list))
        )

        threading.Thread(
            target=self.fast_test_worker,
            daemon=True
        ).start()

    def fast_test_worker(self):

        def on_progress(completed, total, partial_results):
            self.root.after(
                0,
                self.fast_progress,
                completed,
                total,
                partial_results
            )

        results = self.fast_tester.test_many(
            self.dns_list,
            progress_cb=on_progress,
            cancel_flag=lambda: self.cancel_requested
        )

        self.root.after(0, self.finish_fast_test, results)

    def fast_progress(self, completed, total, partial_results):

        self.results = partial_results
        self.table_mode = "results"

        self.progress["value"] = (completed / total) * 100

        self.status_var.set(
            self.t("status.fast_progress", completed=completed, total=total)
        )

        self.refresh_table()

    def finish_fast_test(self, results):

        self.testing = False

        self.enable_buttons()

        self.results = results

        self.refresh_table()

        valid = [
            x for x in self.results
            if x["avg"] is not None and x["success"] > 0
        ]

        if valid:

            best = valid[0]

            self.best_result = best

            self.best_var.set(
                self.t(
                    "best.fastest",
                    name=best["name"],
                    primary=best["primary"],
                    avg=f"{best['avg']:.1f}"
                )
            )

            self.info_var.set(self.t("info.fast_done"))

            self.apply_button.config(state="normal")

            self.status_var.set(
                self.t("status.fast_complete", count=len(valid))
            )

            play_sound("success")

        else:

            self.best_var.set(self.t("best.fastest_none"))

            self.status_var.set(self.t("status.no_dns_responded"))

            play_sound("error")

    # ========================================================
    # FORTNITE TEST
    # ========================================================

    def start_fortnite_test(self):

        if self.testing:
            return

        if not self.results:

            self.start_fast_test()

            messagebox.showinfo(
                self.t("msgbox.step1_title"),
                self.t("msgbox.step1_body")
            )

            return

        candidates = [
            x for x in self.results
            if x.get("avg") is not None
        ][:15]

        if not candidates:

            messagebox.showwarning(
                self.t("msgbox.fortnite_title"),
                self.t("msgbox.no_candidates")
            )

            return

        self.testing = True
        self.cancel_requested = False

        self.disable_buttons()

        self.progress["value"] = 0

        self.status_var.set(
            self.t("status.fortnite_testing", count=len(candidates))
        )

        threading.Thread(
            target=self.fortnite_worker,
            args=(candidates,),
            daemon=True
        ).start()

    def fortnite_worker(self, candidates):

        def on_progress(completed, total, partial_results):
            self.root.after(
                0,
                self.fortnite_progress,
                completed,
                total,
                partial_results
            )

        results = self.fortnite_tester.test_many(
            candidates,
            progress_cb=on_progress,
            cancel_flag=lambda: self.cancel_requested
        )

        self.root.after(0, self.finish_fortnite_test, results)

    def fortnite_progress(self, completed, total, current_results):

        self.progress["value"] = (completed / total) * 100

        self.status_var.set(
            self.t("status.fortnite_progress", completed=completed, total=total)
        )

        self.results = current_results
        self.table_mode = "results"

        self.refresh_table()

    def finish_fortnite_test(self, results):

        self.testing = False

        self.enable_buttons()

        self.results = results

        self.refresh_table()

        if not results:

            self.best_var.set(self.t("best.fortnite_none"))

            play_sound("error")

            return

        best = results[0]

        if best["score"] == float("inf"):

            self.best_var.set(self.t("best.fortnite_invalid"))

            self.status_var.set(self.t("status.fortnite_unreachable"))

            play_sound("error")

            return

        self.best_result = best

        valid = [
            x for x in best["fortnite"]
            if x["avg"] is not None
        ]

        if valid:

            avg = statistics.mean(x["avg"] for x in valid)
            losses = statistics.mean(x["loss"] for x in valid)

        else:

            avg = 0
            losses = 100

        self.best_var.set(
            self.t(
                "best.fortnite_best",
                name=best["name"],
                primary=best["primary"]
            )
        )

        self.info_var.set(
            self.t(
                "info.fortnite_summary",
                avg=f"{avg:.1f}",
                loss=f"{losses:.1f}",
                score=f"{best['score']:.1f}"
            )
        )

        self.status_var.set(self.t("status.fortnite_complete"))

        self.apply_button.config(state="normal")

        play_sound("success")

    # ========================================================
    # REALITY CHECK (TCP-based sanity check)
    # ========================================================

    def start_reality_check(self):

        if self.testing:
            return

        if not self.best_result or not self.best_result.get("fortnite"):

            messagebox.showwarning(
                self.t("reality.title"),
                self.t("reality.need_test")
            )

            return

        self.testing = True
        self.disable_buttons()

        self.status_var.set(self.t("status.reality_checking"))

        threading.Thread(
            target=self.reality_check_worker,
            args=(self.best_result,),
            daemon=True
        ).start()

    def reality_check_worker(self, best_result):

        rows = []

        for region in best_result["fortnite"]:

            ip = region.get("ip")

            tcp_result = (
                self.tcp_pinger.ping(ip, count=4)
                if ip
                else {"avg": None, "loss": 100.0}
            )

            rows.append((
                region["region"],
                region.get("avg"),
                tcp_result.get("avg"),
                tcp_result.get("loss")
            ))

        self.root.after(0, self.finish_reality_check, rows)

    def finish_reality_check(self, rows):

        self.testing = False
        self.enable_buttons()

        self.status_var.set(self.t("status.reality_done"))

        self.show_reality_result(rows)

    def show_reality_result(self, rows):

        win = tk.Toplevel(self.root)
        win.title(self.t("reality.title"))
        win.configure(bg=theme.CARD)
        win.resizable(False, False)
        win.transient(self.root)

        columns = ("region", "icmp", "tcp", "loss")

        tree = ttk.Treeview(win, columns=columns, show="headings", height=len(rows))

        tree.heading("region", text=self.t("reality.col.region"))
        tree.heading("icmp", text=self.t("reality.col.icmp"))
        tree.heading("tcp", text=self.t("reality.col.tcp"))
        tree.heading("loss", text=self.t("reality.col.loss"))

        for col in columns:
            tree.column(col, width=150, anchor="center")

        for region, icmp_avg, tcp_avg, tcp_loss in rows:

            icmp_text = f"{icmp_avg:.0f} ms" if icmp_avg is not None else self.t("table.fail")
            tcp_text = f"{tcp_avg:.0f} ms" if tcp_avg is not None else self.t("table.fail")
            loss_text = f"{tcp_loss:.0f}%" if tcp_loss is not None else "-"

            tree.insert("", "end", values=(region, icmp_text, tcp_text, loss_text))

        tree.pack(padx=15, pady=15)

        tk.Label(
            win,
            text=self.t("reality.explain"),
            bg=theme.CARD,
            fg=theme.MUTED,
            font=("Segoe UI", 9),
            justify="left",
            wraplength=520
        ).pack(padx=15, pady=(0, 15))

        tk.Button(
            win,
            text=self.t("common.close"),
            command=win.destroy,
            bg=theme.CARD2,
            fg=theme.TEXT,
            activebackground="#475569",
            activeforeground=theme.TEXT,
            relief="flat",
            padx=15,
            pady=6
        ).pack(pady=(0, 15))

    # ========================================================
    # ROUTE CHECK (traceroute diagnostic)
    # ========================================================

    def start_route_check(self):

        if self.testing:
            return

        if not self.best_result or not self.best_result.get("fortnite"):

            messagebox.showwarning(
                self.t("route.title"),
                self.t("route.need_test")
            )

            return

        valid_regions = [
            r for r in self.best_result["fortnite"]
            if r.get("ip") and r.get("avg") is not None
        ]

        if not valid_regions:

            messagebox.showwarning(
                self.t("route.title"),
                self.t("route.need_test")
            )

            return

        best_region = min(valid_regions, key=lambda r: r["avg"])

        self.testing = True
        self.disable_buttons()

        self.status_var.set(self.t("route.checking"))

        threading.Thread(
            target=self.route_check_worker,
            args=(best_region,),
            daemon=True
        ).start()

    def route_check_worker(self, region):

        hops = self.route_tracer.trace(region["ip"])
        bottleneck = self.route_tracer.find_bottleneck(hops)

        self.root.after(
            0,
            self.finish_route_check,
            region,
            hops,
            bottleneck
        )

    def finish_route_check(self, region, hops, bottleneck):

        self.testing = False
        self.enable_buttons()

        self.status_var.set(self.t("route.done"))

        self.show_route_result(region, hops, bottleneck)

    def show_route_result(self, region, hops, bottleneck):

        win = tk.Toplevel(self.root)
        win.title(f"{self.t('route.title')} — {region['region']} ({region['ip']})")
        win.configure(bg=theme.CARD)
        win.resizable(False, False)
        win.transient(self.root)

        columns = ("hop", "ip", "time")

        tree = ttk.Treeview(
            win,
            columns=columns,
            show="headings",
            height=min(len(hops), 20) or 1
        )

        tree.heading("hop", text=self.t("route.col.hop"))
        tree.heading("ip", text=self.t("route.col.ip"))
        tree.heading("time", text=self.t("route.col.time"))

        tree.column("hop", width=60, anchor="center")
        tree.column("ip", width=160, anchor="center")
        tree.column("time", width=120, anchor="center")

        timeout_text = self.t("route.timeout")

        for hop in hops:

            time_text = (
                f"{hop['avg_ms']:.0f} ms"
                if hop["avg_ms"] is not None
                else timeout_text
            )

            row_id = tree.insert(
                "",
                "end",
                values=(hop["hop"], hop["ip"] or "-", time_text)
            )

            if bottleneck and hop["hop"] == bottleneck["hop"]:
                tree.item(row_id, tags=("bottleneck",))

        tree.tag_configure("bottleneck", background="#7c2d12", foreground=theme.WHITE)

        tree.pack(padx=15, pady=15)

        if bottleneck:

            note = self.t(
                "route.bottleneck_found",
                hop=bottleneck["hop"],
                ip=bottleneck["ip"] or "?"
            )

        else:

            note = self.t("route.bottleneck_none")

        tk.Label(
            win,
            text=note,
            bg=theme.CARD,
            fg=theme.YELLOW,
            font=("Segoe UI", 9, "bold"),
            justify="left",
            wraplength=520
        ).pack(padx=15, pady=(0, 8))

        tk.Label(
            win,
            text=self.t("route.explain"),
            bg=theme.CARD,
            fg=theme.MUTED,
            font=("Segoe UI", 9),
            justify="left",
            wraplength=520
        ).pack(padx=15, pady=(0, 15))

        tk.Button(
            win,
            text=self.t("common.close"),
            command=win.destroy,
            bg=theme.CARD2,
            fg=theme.TEXT,
            activebackground="#475569",
            activeforeground=theme.TEXT,
            relief="flat",
            padx=15,
            pady=6
        ).pack(pady=(0, 15))

    # ========================================================
    # APPLY
    # ========================================================

    def apply_selected(self, event=None):

        selection = self.tree.selection()

        if not selection:
            return

        index = self.tree.index(selection[0])

        record = self.get_row_record(index)

        if record is None:
            return

        self.apply_dns_item(self.ensure_secondary(record))

    def apply_best(self):

        if not self.best_result:

            if self.results:
                self.best_result = self.results[0]

            else:

                messagebox.showwarning(
                    self.t("msgbox.dns_title"),
                    self.t("msgbox.run_test_first")
                )

                return

        self.apply_dns_item(self.ensure_secondary(self.best_result))

    def apply_dns_item(self, item):

        adapter = self.adapter_var.get()

        if not adapter:

            messagebox.showwarning(
                self.t("msgbox.adapter_title"),
                self.t("msgbox.select_adapter")
            )

            return

        if not is_admin():

            answer = messagebox.askyesno(
                self.t("msgbox.admin_title"),
                self.t("msgbox.admin_needed_apply")
            )

            if answer:

                # The elevated relaunch is a brand new process with
                # an empty DNS list and no test results. Without
                # this, the user has to redo the whole test after
                # the UAC prompt just to click Apply again. Persist
                # the pending choice so the elevated process can
                # finish the job on its own (see check_pending_apply).
                self.config_store.set_pending_apply(adapter, item)

                self.restart_as_admin()

            return

        old_dns = self.network.get_current_dns(adapter)

        self.config_store.record_applied(adapter, old_dns, item)

        secondary = item.get("secondary", "")

        success, message = self.network.set_dns(
            adapter,
            item["primary"],
            secondary
        )

        if success:

            self.update_current_dns()

            play_sound("success")

            messagebox.showinfo(
                self.t("msgbox.dns_applied_title"),
                self.t(
                    "msgbox.dns_applied_manual",
                    name=item["name"],
                    primary=item["primary"],
                    secondary=secondary or self.t("msgbox.na"),
                    adapter=adapter
                )
            )

        else:

            play_sound("error")

            messagebox.showerror(
                self.t("msgbox.dns_error_title"),
                message
            )

    # ========================================================
    # CLEAR / DHCP
    # ========================================================

    def clear_dns(self):

        adapter = self.adapter_var.get()

        if not adapter:

            messagebox.showwarning(
                self.t("msgbox.adapter_title"),
                self.t("msgbox.select_adapter")
            )

            return

        answer = messagebox.askyesno(
            self.t("msgbox.clear_title"),
            self.t("msgbox.clear_confirm")
        )

        if not answer:
            return

        if not is_admin():

            answer = messagebox.askyesno(
                self.t("msgbox.admin_title"),
                self.t("msgbox.admin_needed_clear")
            )

            if answer:
                self.restart_as_admin()

            return

        success, message = self.network.clear_dns(adapter)

        if success:

            self.update_current_dns()

            play_sound("success")

            messagebox.showinfo(
                self.t("msgbox.dns_cleared_title"),
                message
            )

        else:

            play_sound("error")

            messagebox.showerror(
                self.t("msgbox.dns_error_title"),
                message
            )

    # ========================================================
    # ADMIN
    # ========================================================

    def restart_as_admin(self):

        try:

            if relaunch_as_admin():
                self.root.destroy()

            # else: user declined the UAC prompt — keep running
            # unelevated rather than silently vanishing.

        except Exception as e:

            messagebox.showerror(
                self.t("msgbox.admin_title"),
                str(e)
            )

    # ========================================================
    # BUTTON STATES
    # ========================================================

    def disable_buttons(self):

        self.fast_button.config(state="disabled")
        self.fortnite_button.config(state="disabled")
        self.online_button.config(state="disabled")
        self.reality_button.config(state="disabled")
        self.route_button.config(state="disabled")
        self.cancel_button.config(state="normal")

    def enable_buttons(self):

        self.fast_button.config(state="normal")
        self.fortnite_button.config(state="normal")
        self.online_button.config(state="normal")
        self.reality_button.config(state="normal")
        self.route_button.config(state="normal")
        self.cancel_button.config(state="disabled")

    def cancel_test(self):

        if not self.testing:
            return

        self.cancel_requested = True

        self.status_var.set(self.t("status.cancelling"))
