import os

from . import APP_NAME, VERSION  # noqa: F401  (re-exported for convenience)

CONFIG_FILE = os.path.join(
    os.path.expanduser("~"),
    ".fortnite_dns_optimizer.json"
)

# Shown in the About dialog. AUTHOR_NAME is a best-guess default —
# correct it if it's wrong. AUTHOR_LINK and DONATE_URL are left
# blank on purpose (real Zarinpal link to be added later); the About
# dialog shows a "coming soon" message for whichever one is empty.
AUTHOR_NAME = "Mohammad Ali"
AUTHOR_EMAIL = "mr.mirshahbazi@gmail.com"
AUTHOR_LINK = ""
DONATE_URL = ""

# Used when the DNS the user is applying has no secondary of its
# own (e.g. a scraped online entry, or a manual one left blank) —
# Cloudflare's secondary is fast, globally anycast, and about as
# safe a fallback as exists, so the adapter never ends up with only
# one DNS server configured (no failover) after "Apply".
DEFAULT_FALLBACK_SECONDARY = "1.0.0.1"

ONLINE_DNS_URLS = [
    # Community DNS list
    "https://raw.githubusercontent.com/RichieChill/dns_server_list/master/dns_server_list.md",

    # DNSCrypt public resolver list
    "https://raw.githubusercontent.com/DNSCrypt/dnscrypt-resolvers/master/v3/public-resolvers.md",
]

# Official Epic/Fortnite latency endpoints
FORTNITE_ENDPOINTS = {
    "Bahrain": "ping-bah.ds.on.epicgames.com",
    "Israel": "ping-il.ds.on.epicgames.com",
    "Germany": "ping-de.ds.on.epicgames.com",
    "France": "ping-fr.ds.on.epicgames.com",
    "United Kingdom": "ping-gb.ds.on.epicgames.com",
    "Mumbai": "ping-mum.ds.on.epicgames.com",
    "Tokyo": "ping-tok.ds.on.epicgames.com",
    "Oregon": "ping-or.ds.on.epicgames.com",
    "Virginia": "ping-va.ds.on.epicgames.com",
}

# Built-in fallback list.
# Even if the online list fails to download, the program still works.
BUILTIN_DNS = [
    ("Cloudflare", "1.1.1.1", "1.0.0.1"),
    ("Google", "8.8.8.8", "8.8.4.4"),
    ("Quad9", "9.9.9.9", "149.112.112.112"),
    ("AdGuard", "94.140.14.14", "94.140.15.15"),
    ("OpenDNS", "208.67.222.222", "208.67.220.220"),

    ("Shecan", "178.22.122.100", "185.51.200.2"),
    ("Radar", "10.202.10.10", "10.202.10.11"),
    ("403.online", "10.202.10.202", "10.202.10.102"),
    ("Electro", "78.157.42.100", "78.157.42.101"),
    ("Begzar", "185.55.226.26", "185.55.225.25"),

    ("Level3", "4.2.2.1", "4.2.2.2"),
    ("Verisign", "64.6.64.6", "64.6.65.6"),
    ("CleanBrowsing", "185.228.168.9", "185.228.169.9"),
    ("Comodo", "8.26.56.26", "8.20.247.20"),
    ("Alternate DNS", "76.76.19.19", "76.223.122.150"),
    ("Yandex", "77.88.8.8", "77.88.8.1"),
    ("DNS.WATCH", "84.200.69.80", "84.200.70.40"),
    ("Freenom World", "80.80.80.80", "80.80.81.81"),
]

FAST_QUERIES = [
    "example.com",
    "google.com",
    "cloudflare.com",
]

# Iran has no direct Epic PoP, so the regions closest to it
# (Bahrain, Mumbai) are the most relevant besides the classic
# Europe/Middle East set.
FORTNITE_REGIONS = [
    "Bahrain",
    "Mumbai",
    "Israel",
    "Germany",
    "United Kingdom",
]

DNS_TIMEOUT = 2.0

FAST_QUERY_COUNT = 3

FORTNITE_PING_COUNT = 4

MAX_WORKERS = 16

# Fortnite candidates are tested with real ping subprocesses across
# several regions each; too much parallelism just thrashes the
# network stack, so this stays much lower than MAX_WORKERS.
MAX_FORTNITE_WORKERS = 4
