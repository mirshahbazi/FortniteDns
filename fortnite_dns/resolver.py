import time

from .constants import DNS_TIMEOUT
from .utils import is_ipv4, normalize_ip

try:
    import dns.resolver as _dns_resolver_module
except ImportError:
    _dns_resolver_module = None


class DnsResolver:
    """
    Resolves a hostname against one specific DNS server (not the
    system resolver), timing how long it takes. This is the piece
    every test in the app is built on, and the one most worth
    isolating: a fake resolver makes FastDnsTester/FortniteDnsTester
    testable without touching a real network.
    """

    def __init__(self, timeout=DNS_TIMEOUT):
        self.timeout = timeout

    @staticmethod
    def is_available():
        return _dns_resolver_module is not None

    def resolve(self, hostname, dns_server):

        if _dns_resolver_module is None:
            return None, None

        resolver = _dns_resolver_module.Resolver(
            configure=False
        )

        resolver.nameservers = [
            dns_server
        ]

        resolver.timeout = self.timeout
        resolver.lifetime = self.timeout

        start = time.perf_counter()

        try:

            answers = resolver.resolve(
                hostname,
                "A"
            )

            elapsed = (
                time.perf_counter()
                - start
            ) * 1000

            ips = []

            for answer in answers:

                ip = normalize_ip(
                    answer.to_text()
                )

                if is_ipv4(ip):
                    ips.append(ip)

            return ips, elapsed

        except Exception:

            return [], (
                time.perf_counter()
                - start
            ) * 1000
