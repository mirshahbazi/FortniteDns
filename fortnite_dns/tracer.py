import re

from .utils import run_command


class RouteTracer:
    """
    Wraps Windows `tracert` and parses hop-by-hop latency. This
    can't fix a slow international route — nothing running on the
    user's own PC can — but it can show *where* along the path the
    latency actually appears, which is the difference between
    "some DNS server is slow" and "my ISP's international gateway
    is congested/throttled," and only one of those is something a
    DNS choice could ever have influenced.
    """

    def __init__(self, max_hops=20, timeout_ms=800):
        self.max_hops = max_hops
        self.timeout_ms = timeout_ms

    def trace(self, ip):

        command = [
            "tracert",
            "-h", str(self.max_hops),
            "-w", str(self.timeout_ms),
            "-d",
            ip
        ]

        # Generous timeout: worst case every hop times out on every
        # probe (3 probes/hop by default).
        subprocess_timeout = self.max_hops * (self.timeout_ms / 1000) * 3 + 15

        code, stdout, stderr = run_command(
            command,
            timeout=subprocess_timeout
        )

        return self.parse(stdout)

    @staticmethod
    def parse(output):

        hops = []

        for line in (output or "").splitlines():

            line = line.strip()

            match = re.match(r"^(\d+)\s+(.*)$", line)

            if not match:
                continue

            hop_num = int(match.group(1))
            rest = match.group(2)

            ip_match = re.search(
                r"(\d{1,3}(?:\.\d{1,3}){3})",
                rest
            )

            hop_ip = ip_match.group(1) if ip_match else None

            raw_times = re.findall(r"<?\s*(\d+)\s*ms", rest)

            if not raw_times:

                # A fully timed-out hop ("* * *") still shows where
                # in the path things went dark.
                if "*" in rest:
                    hops.append({
                        "hop": hop_num,
                        "ip": hop_ip,
                        "avg_ms": None,
                        "timeout": True
                    })

                continue

            values = [float(t) for t in raw_times]

            hops.append({
                "hop": hop_num,
                "ip": hop_ip,
                "avg_ms": sum(values) / len(values),
                "timeout": False
            })

        return hops

    @staticmethod
    def find_bottleneck(hops, jump_threshold_ms=60):
        """
        Returns the first hop where latency jumps by at least
        `jump_threshold_ms` versus the previous responding hop —
        a simple heuristic for "this is roughly where it got slow",
        not a certainty (routing isn't always symmetric and a
        single hop's own ICMP handling can be misleadingly slow).
        """

        previous = 0.0

        for hop in hops:

            if hop["avg_ms"] is None:
                continue

            if hop["avg_ms"] - previous >= jump_threshold_ms:
                return hop

            previous = hop["avg_ms"]

        return None
