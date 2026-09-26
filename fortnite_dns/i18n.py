"""
Minimal string-table based i18n. No RTL widget reordering (Tkinter
can't do that cleanly) — Persian text is simply rendered left-to-
right within otherwise unchanged layout. Good enough for labels,
buttons and dialogs; not a substitute for a real RTL toolkit.
"""

DEFAULT_LANGUAGE = "fa"

LANGUAGE_NAMES = {
    "fa": "فارسی",
    "en": "English",
}

TRANSLATIONS = {
    "en": {
        "app.title": "Fortnite DNS Optimizer",
        "app.subtitle": "DNS Jumper style benchmark + Fortnite/Epic latency verification",

        "label.adapter": "Adapter:",
        "button.update_dns_list": "☁ Update DNS List",
        "button.updating": "Updating...",
        "button.fast_test": "⚡ FAST TEST",
        "button.fortnite_test": "🎮 FORTNITE TEST",
        "button.apply_best": "✓ APPLY BEST",
        "button.clear_dns": "✕ CLEAR / DHCP",
        "button.cancel": "⏹ CANCEL",
        "button.reality_check": "🔎 REAL PING CHECK",
        "button.about": "ℹ️ About",
        "button.language": "🌐 فارسی",

        "label.add_manual_dns": "Add Manual DNS:",
        "label.manual_hint": "(name / primary IP / secondary IP)",
        "button.add": "+ Add",

        "status.loading": "Loading DNS list...",
        "status.loaded_count": "{count} DNS servers loaded.",
        "status.loaded_with_online": "{count} DNS servers loaded ({online} from online sources).",
        "status.downloading_online": "Downloading online DNS list...",
        "status.online_unavailable": "Online list unavailable. Built-in list kept.",
        "status.updated_count": "Updated: {count} DNS servers.",
        "status.added_custom": "Added custom DNS '{name}'. {count} servers loaded.",
        "status.fast_testing": "Fast Test: testing {count} DNS servers...",
        "status.fast_progress": "Fast Test: {completed}/{total}",
        "status.fast_complete": "Fast Test complete: {count} working DNS.",
        "status.no_dns_responded": "No DNS server responded.",
        "status.fortnite_testing": "Fortnite Test: verifying {count} candidates...",
        "status.fortnite_progress": "Fortnite Test: {completed}/{total}",
        "status.fortnite_complete": "Fortnite Test completed.",
        "status.fortnite_unreachable": "Fortnite endpoints could not be reached.",
        "status.cancelling": "Cancelling... finishing in-flight checks.",
        "status.current_dns_prefix": "Current DNS: ",
        "status.current_dns_none": "No active adapter",
        "status.current_dns_dhcp": "Automatic / DHCP",
        "status.reality_checking": "Running a TCP-based reality check on the best DNS...",
        "status.reality_done": "Real ping check finished.",

        "info.default": "Fast Test checks DNS resolution. Fortnite Test verifies Epic endpoints.",
        "info.fast_done": "Fast Test finished. For Fortnite-specific selection, run FORTNITE TEST.",
        "info.fortnite_summary": "Epic Endpoint Average: {avg} ms   |   Loss: {loss}%   |   Score: {score}",

        "best.initial": "🏆 Best: -",
        "best.fastest_none": "🏆 Fastest DNS: None",
        "best.fastest": "🏆 Fastest DNS: {name} ({primary}) — {avg} ms",
        "best.fortnite_none": "🏆 Fortnite DNS: None",
        "best.fortnite_invalid": "🏆 Fortnite DNS: No valid result",
        "best.fortnite_best": "🏆 Fortnite Best DNS: {name} ({primary})",

        "table.col.name": "DNS",
        "table.col.dns": "Address",
        "table.col.fast": "Fast DNS",
        "table.col.success": "Success",
        "table.col.bahrain": "Bahrain",
        "table.col.mumbai": "Mumbai",
        "table.col.israel": "Israel",
        "table.col.germany": "Germany",
        "table.col.uk": "UK",
        "table.col.score": "Score",
        "table.col.status": "Status",
        "table.status.ready": "Ready",
        "table.status.ok": "OK",
        "table.fail": "FAIL",

        "footer.disclaimer": (
            "ICMP latency is not guaranteed to equal Fortnite's actual "
            "UDP in-game ping — use REAL PING CHECK for a closer sanity check."
        ),

        "menu.apply_both": "Set as Primary + Secondary",
        "menu.set_primary": "Set as Primary only",
        "menu.set_secondary": "Set as Secondary only",

        "msgbox.dns_title": "DNS",
        "msgbox.no_dns_loaded": "No DNS servers are loaded.",
        "msgbox.adapter_title": "Adapter",
        "msgbox.select_adapter": "Select a network adapter.",
        "msgbox.custom_dns_title": "Custom DNS",
        "msgbox.invalid_primary": "Enter a valid primary IPv4 address.",
        "msgbox.invalid_secondary": "Secondary address is invalid.",
        "msgbox.step1_title": "Step 1 complete",
        "msgbox.step1_body": (
            "First run FAST TEST.\n\n"
            "When it finishes, press FORTNITE TEST again."
        ),
        "msgbox.fortnite_title": "Fortnite Test",
        "msgbox.no_candidates": "No working DNS candidates.",
        "msgbox.run_test_first": "Run a test first.",
        "msgbox.admin_title": "Administrator",
        "msgbox.admin_needed_apply": (
            "Changing DNS requires Administrator permission.\n\n"
            "Restart as Administrator?"
        ),
        "msgbox.admin_needed_clear": (
            "Administrator permission is required.\n\n"
            "Restart as Administrator?"
        ),
        "msgbox.dns_applied_title": "DNS Applied",
        "msgbox.dns_applied_auto": (
            "DNS was applied automatically after restarting as "
            "Administrator.\n\n"
            "Provider: {name}\nPrimary: {primary}\nSecondary: {secondary}\n\n"
            "Adapter: {adapter}"
        ),
        "msgbox.dns_applied_manual": (
            "DNS applied successfully.\n\n"
            "Provider: {name}\nPrimary: {primary}\nSecondary: {secondary}\n\n"
            "Adapter: {adapter}"
        ),
        "msgbox.dns_error_title": "DNS Error",
        "msgbox.clear_title": "Clear DNS",
        "msgbox.clear_confirm": (
            "Reset DNS to Automatic/DHCP?\n\n"
            "Your ISP/router DNS will be used again."
        ),
        "msgbox.dns_cleared_title": "DNS Cleared",
        "msgbox.na": "N/A",
        "msgbox.set_primary_first": "Set a primary DNS on this adapter first.",

        "about.title": "About",
        "about.version": "Version",
        "about.author": "Author",
        "about.donate_title": "Support the project",
        "about.donate_link_text": "Donate via Zarinpal",
        "about.donate_coming_soon": "Donation link coming soon.",
        "common.close": "Close",

        "reality.title": "Real Ping Check",
        "reality.need_test": "Run the Fortnite Test first so there's a result to double-check.",
        "reality.explain": (
            "This does a TCP handshake to each region's resolved IP on "
            "port 443 instead of an ICMP ping. Many providers answer plain "
            "ICMP from a nearby edge node without it reaching the real "
            "backend, which can under-report latency; a TCP connection "
            "must complete a full round trip to that exact server. It is "
            "still not identical to Fortnite's own UDP game traffic, but "
            "it is a much closer sanity check than ICMP alone.\n\n"
            "If both numbers here are low but in-game ping is still very "
            "high, the bottleneck is most likely international routing "
            "from your ISP to Epic's servers — something DNS choice can't "
            "fix, since DNS only affects hostname lookup, not the actual "
            "game traffic path."
        ),
        "reality.col.region": "Region",
        "reality.col.icmp": "ICMP (this app)",
        "reality.col.tcp": "TCP RTT (real path)",
        "reality.col.loss": "TCP Loss",

        "button.route_check": "🛰 ROUTE CHECK",
        "route.title": "Network Route Check",
        "route.need_test": "Run the Fortnite Test first so there's a region IP to trace.",
        "route.checking": "Tracing the route to the best Fortnite region (this can take ~15-30s)...",
        "route.done": "Route check finished.",
        "route.col.hop": "Hop",
        "route.col.ip": "IP",
        "route.col.time": "Latency",
        "route.timeout": "(no response)",
        "route.bottleneck_found": (
            "Latency jumps sharply at hop {hop} ({ip}) — that's most "
            "likely where the real bottleneck is, not your DNS choice."
        ),
        "route.bottleneck_none": (
            "No single sharp jump found — latency looks like it "
            "builds up gradually across the path."
        ),
        "route.explain": (
            "This traces the actual network path to Epic's server, hop "
            "by hop. It can't fix a slow international route — nothing "
            "running on your own PC can, and DNS choice has no effect on "
            "it either, since DNS only resolves a name, it doesn't carry "
            "game traffic. But it tells you WHERE the delay is coming "
            "from: if the jump happens right at your ISP's international "
            "gateway (usually one of the first few hops after your "
            "router), that's a routing/congestion issue on your ISP's "
            "side — the kind of problem a dedicated gaming tunnel/VPN "
            "service is built to route around, not a DNS optimizer."
        ),
    },
    "fa": {
        "app.title": "بهینه‌ساز DNS فورتنایت",
        "app.subtitle": "بنچمارک شبیه DNS Jumper + سنجش پینگ واقعی سرورهای اپیک/فورتنایت",

        "label.adapter": "آداپتور:",
        "button.update_dns_list": "☁ به‌روزرسانی لیست DNS",
        "button.updating": "در حال به‌روزرسانی...",
        "button.fast_test": "⚡ تست سریع",
        "button.fortnite_test": "🎮 تست فورتنایت",
        "button.apply_best": "✓ اعمال بهترین",
        "button.clear_dns": "✕ پاک‌کردن / DHCP",
        "button.cancel": "⏹ لغو",
        "button.reality_check": "🔎 بررسی پینگ واقعی",
        "button.about": "ℹ️ درباره",
        "button.language": "🌐 English",

        "label.add_manual_dns": "افزودن DNS دستی:",
        "label.manual_hint": "(نام / آی‌پی اصلی / آی‌پی کمکی)",
        "button.add": "+ افزودن",

        "status.loading": "در حال بارگذاری لیست DNS...",
        "status.loaded_count": "{count} سرور DNS بارگذاری شد.",
        "status.loaded_with_online": "{count} سرور DNS بارگذاری شد ({online} مورد از منابع آنلاین).",
        "status.downloading_online": "در حال دانلود لیست آنلاین DNS...",
        "status.online_unavailable": "لیست آنلاین در دسترس نبود. لیست پیش‌فرض حفظ شد.",
        "status.updated_count": "به‌روزرسانی شد: {count} سرور DNS.",
        "status.added_custom": "DNS دستی «{name}» اضافه شد. {count} سرور بارگذاری شد.",
        "status.fast_testing": "تست سریع: در حال بررسی {count} سرور DNS...",
        "status.fast_progress": "تست سریع: {completed}/{total}",
        "status.fast_complete": "تست سریع تمام شد: {count} DNS سالم.",
        "status.no_dns_responded": "هیچ سروری پاسخ نداد.",
        "status.fortnite_testing": "تست فورتنایت: در حال بررسی {count} کاندید...",
        "status.fortnite_progress": "تست فورتنایت: {completed}/{total}",
        "status.fortnite_complete": "تست فورتنایت تمام شد.",
        "status.fortnite_unreachable": "سرورهای فورتنایت در دسترس نبودند.",
        "status.cancelling": "در حال لغو... بررسی‌های درحال‌انجام تمام می‌شود.",
        "status.current_dns_prefix": "DNS فعلی: ",
        "status.current_dns_none": "آداپتور فعالی وجود ندارد",
        "status.current_dns_dhcp": "خودکار / DHCP",
        "status.reality_checking": "در حال اجرای بررسی واقعی (TCP) روی بهترین DNS...",
        "status.reality_done": "بررسی پینگ واقعی تمام شد.",

        "info.default": "تست سریع، سرعت resolve شدن DNS را می‌سنجد. تست فورتنایت پینگ واقعی سرورهای اپیک را بررسی می‌کند.",
        "info.fast_done": "تست سریع تمام شد. برای انتخاب اختصاصی فورتنایت، تست فورتنایت را اجرا کن.",
        "info.fortnite_summary": "میانگین پینگ سرورهای اپیک: {avg} ms   |   افت پکت: {loss}%   |   امتیاز: {score}",

        "best.initial": "🏆 بهترین: -",
        "best.fastest_none": "🏆 سریع‌ترین DNS: هیچ‌کدام",
        "best.fastest": "🏆 سریع‌ترین DNS: {name} ({primary}) — {avg} ms",
        "best.fortnite_none": "🏆 DNS فورتنایت: هیچ‌کدام",
        "best.fortnite_invalid": "🏆 DNS فورتنایت: نتیجه معتبری نبود",
        "best.fortnite_best": "🏆 بهترین DNS فورتنایت: {name} ({primary})",

        "table.col.name": "DNS",
        "table.col.dns": "آدرس",
        "table.col.fast": "تست سریع",
        "table.col.success": "موفقیت",
        "table.col.bahrain": "بحرین",
        "table.col.mumbai": "بمبئی",
        "table.col.israel": "اسرائیل",
        "table.col.germany": "آلمان",
        "table.col.uk": "انگلستان",
        "table.col.score": "امتیاز",
        "table.col.status": "وضعیت",
        "table.status.ready": "آماده",
        "table.status.ok": "سالم",
        "table.fail": "ناموفق",

        "footer.disclaimer": (
            "پینگ ICMP لزوماً برابر با پینگ واقعی UDP داخل بازی فورتنایت "
            "نیست — برای مقایسه دقیق‌تر از «بررسی پینگ واقعی» استفاده کن."
        ),

        "menu.apply_both": "ست‌کردن به‌عنوان اصلی + کمکی",
        "menu.set_primary": "ست‌کردن فقط به‌عنوان اصلی",
        "menu.set_secondary": "ست‌کردن فقط به‌عنوان کمکی",

        "msgbox.dns_title": "DNS",
        "msgbox.no_dns_loaded": "هیچ سرور DNSای بارگذاری نشده.",
        "msgbox.adapter_title": "آداپتور",
        "msgbox.select_adapter": "یک آداپتور شبکه انتخاب کن.",
        "msgbox.custom_dns_title": "DNS دستی",
        "msgbox.invalid_primary": "یک آی‌پی IPv4 معتبر برای DNS اصلی وارد کن.",
        "msgbox.invalid_secondary": "آی‌پی کمکی نامعتبر است.",
        "msgbox.step1_title": "مرحله ۱ کامل شد",
        "msgbox.step1_body": (
            "اول تست سریع را اجرا کن.\n\n"
            "وقتی تمام شد، دوباره روی تست فورتنایت بزن."
        ),
        "msgbox.fortnite_title": "تست فورتنایت",
        "msgbox.no_candidates": "هیچ DNS سالمی برای تست پیدا نشد.",
        "msgbox.run_test_first": "اول یک تست اجرا کن.",
        "msgbox.admin_title": "دسترسی ادمین",
        "msgbox.admin_needed_apply": (
            "تغییر DNS نیاز به دسترسی ادمین دارد.\n\n"
            "با دسترسی ادمین دوباره اجرا شود؟"
        ),
        "msgbox.admin_needed_clear": (
            "دسترسی ادمین لازم است.\n\n"
            "با دسترسی ادمین دوباره اجرا شود؟"
        ),
        "msgbox.dns_applied_title": "DNS اعمال شد",
        "msgbox.dns_applied_auto": (
            "DNS به‌صورت خودکار بعد از اجرای مجدد با دسترسی ادمین اعمال شد.\n\n"
            "سرویس: {name}\nاصلی: {primary}\nکمکی: {secondary}\n\n"
            "آداپتور: {adapter}"
        ),
        "msgbox.dns_applied_manual": (
            "DNS با موفقیت اعمال شد.\n\n"
            "سرویس: {name}\nاصلی: {primary}\nکمکی: {secondary}\n\n"
            "آداپتور: {adapter}"
        ),
        "msgbox.dns_error_title": "خطای DNS",
        "msgbox.clear_title": "پاک‌کردن DNS",
        "msgbox.clear_confirm": (
            "DNS به حالت خودکار/DHCP برگردد؟\n\n"
            "دوباره از DNS مودم/ISP استفاده می‌شود."
        ),
        "msgbox.dns_cleared_title": "DNS پاک شد",
        "msgbox.na": "ندارد",
        "msgbox.set_primary_first": "اول یک DNS اصلی روی این آداپتور ست کن.",

        "about.title": "درباره",
        "about.version": "نسخه",
        "about.author": "سازنده",
        "about.donate_title": "حمایت از پروژه",
        "about.donate_link_text": "حمایت مالی از طریق زرین‌پال",
        "about.donate_coming_soon": "لینک حمایت مالی به‌زودی اضافه می‌شود.",
        "common.close": "بستن",

        "reality.title": "بررسی پینگ واقعی",
        "reality.need_test": "اول تست فورتنایت را اجرا کن تا نتیجه‌ای برای بررسی وجود داشته باشد.",
        "reality.explain": (
            "این بررسی به‌جای پینگ ICMP، یک اتصال TCP روی پورت ۴۴۳ به آی‌پی "
            "resolve‌شده‌ی هر ریجن می‌زند. خیلی از سرویس‌دهنده‌ها به پینگ ساده "
            "(ICMP) از نزدیک‌ترین نقطه پاسخ می‌دهند بدون این‌که واقعاً به سرور "
            "اصلی برسد، و همین باعث می‌شود عدد واقعی‌تر از چیزی که هست به‌نظر "
            "برسد؛ اما یک اتصال TCP باید کامل تا همان سرور رفت‌وبرگشت داشته "
            "باشد. این هم دقیقاً همان مسیر UDP بازی فورتنایت نیست، ولی خیلی "
            "به واقعیت نزدیک‌تر از ICMP تنهاست.\n\n"
            "اگر این عددها هم پایین باشند ولی پینگ داخل بازی همچنان خیلی "
            "بالاست، احتمال زیاد مشکل از مسیر بین‌الملل ISP تا سرورهای اپیک "
            "است — چیزی که با تغییر DNS درست نمی‌شود، چون DNS فقط روی "
            "resolve‌شدن نام دامنه اثر دارد، نه مسیر واقعی ترافیک بازی."
        ),
        "reality.col.region": "ریجن",
        "reality.col.icmp": "ICMP (این برنامه)",
        "reality.col.tcp": "TCP RTT (مسیر واقعی)",
        "reality.col.loss": "افت پکت TCP",

        "button.route_check": "🛰 بررسی مسیر شبکه",
        "route.title": "بررسی مسیر شبکه",
        "route.need_test": "اول تست فورتنایت را اجرا کن تا یک آی‌پی ریجن برای ترِیس وجود داشته باشد.",
        "route.checking": "در حال ترِیس مسیر تا بهترین ریجن فورتنایت (ممکن است ۱۵ تا ۳۰ ثانیه طول بکشد)...",
        "route.done": "بررسی مسیر تمام شد.",
        "route.col.hop": "هاپ",
        "route.col.ip": "آی‌پی",
        "route.col.time": "تاخیر",
        "route.timeout": "(بدون پاسخ)",
        "route.bottleneck_found": (
            "پرش شدید تاخیر دقیقاً در هاپ {hop} ({ip}) اتفاق می‌افتد — "
            "به‌احتمال زیاد گلوگاه واقعی همین‌جاست، نه انتخاب DNS."
        ),
        "route.bottleneck_none": (
            "پرش شدید و مشخصی پیدا نشد — تاخیر به‌نظر می‌رسد به‌تدریج "
            "در طول مسیر بالا می‌رود."
        ),
        "route.explain": (
            "این ابزار مسیر واقعی شبکه تا سرور اپیک را هاپ‌به‌هاپ ترِیس "
            "می‌کند. این کار یک مسیر بین‌المللی کند را درست نمی‌کند — هیچ "
            "چیزی که روی کامپیوتر خودت اجرا شود نمی‌تواند این کار را بکند، "
            "و انتخاب DNS هم روی آن اثری ندارد چون DNS فقط یک اسم را "
            "resolve می‌کند و ترافیک بازی را جابه‌جا نمی‌کند. اما نشان "
            "می‌دهد تاخیر از کجا شروع می‌شود: اگر پرش دقیقاً همان ابتدای "
            "مسیر (معمولاً یکی از اولین هاپ‌ها بعد از مودم/روتر خودت، یعنی "
            "دروازه‌ی بین‌الملل ISP) اتفاق بیفتد، مشکل مسیریابی/ازدحام "
            "سمت ISP است — دقیقاً همان مشکلی که یک تانل/VPN اختصاصی "
            "گیمینگ برایش ساخته شده، نه یک بهینه‌ساز DNS."
        ),
    },
}


class Translator:

    def __init__(self, language=DEFAULT_LANGUAGE):
        self.language = language if language in TRANSLATIONS else DEFAULT_LANGUAGE

    def set_language(self, language):
        self.language = language if language in TRANSLATIONS else DEFAULT_LANGUAGE

    def other_language(self):
        return "en" if self.language == "fa" else "fa"

    def t(self, key, **kwargs):

        table = TRANSLATIONS.get(self.language, {})

        text = table.get(key)

        if text is None:
            text = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)

        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text

        return text
