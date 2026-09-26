import re
import urllib.error
import urllib.request

from .constants import ONLINE_DNS_URLS
from .utils import is_ipv4


class DnsSourceProvider:
    """
    Where DNS server candidates come from: downloading and parsing
    public lists, and merging them with the built-in/custom ones.
    `download` is a plain instance method (not a free function) so
    a test can subclass/monkeypatch it without touching the network.
    """

    def __init__(self, urls=None, max_online_servers=150):
        self.urls = list(urls) if urls is not None else list(ONLINE_DNS_URLS)
        self.max_online_servers = max_online_servers

    def download(self, url):

        try:

            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent":
                        "FortniteDNSOptimizer/2.1"
                }
            )

            with urllib.request.urlopen(
                request,
                timeout=8
            ) as response:

                return response.read().decode(
                    "utf-8",
                    errors="ignore"
                )

        except Exception:
            return None

    def fetch_online(self):

        all_ips = []

        for url in self.urls:

            text = self.download(url)

            if not text:
                continue

            for ip in self.parse_markdown(text):

                if ip not in all_ips:
                    all_ips.append(ip)

        # Don't allow an insane amount of DNS servers.
        # 150 is plenty for a desktop benchmark.
        all_ips = all_ips[:self.max_online_servers]

        return self.records_from_ips(all_ips)

    @staticmethod
    def parse_markdown(text):
        """
        Extract IPv4 addresses from a large public DNS list.
        """

        if not text:
            return []

        ips = re.findall(
            r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
            text
        )

        result = []

        for ip in ips:

            if is_ipv4(ip) and ip not in result:
                result.append(ip)

        return result

    @staticmethod
    def records_from_ips(ips):

        return [
            (f"Online DNS #{index + 1}", ip, "")
            for index, ip in enumerate(ips)
        ]

    @staticmethod
    def merge(*lists):

        result = []

        seen = set()

        for dns_list in lists:

            for item in dns_list:

                if len(item) < 3:
                    continue

                name = str(item[0]).strip()
                primary = str(item[1]).strip()
                secondary = str(item[2]).strip()

                if not is_ipv4(primary):
                    continue

                if primary in seen:
                    continue

                seen.add(primary)

                result.append((name, primary, secondary))

        return result
