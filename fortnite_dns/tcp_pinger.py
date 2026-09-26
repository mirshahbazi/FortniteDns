import socket
import statistics
import time


class TcpPinger:
    """
    Times a raw TCP handshake (SYN / SYN-ACK / ACK) to host:port,
    instead of an ICMP echo.

    This exists because ICMP ping and real game traffic don't always
    take the same path: some networks/CDNs answer a plain ICMP echo
    from a nearby edge node without it ever reaching the actual
    backend, which can make ICMP ping look far better than the real
    path is. A TCP connection has to complete a full round trip to
    that exact server, so it can't be short-circuited the same way —
    it's a much closer (though still not perfect) proxy for real
    network latency than ICMP alone. It is still not identical to
    Fortnite's own UDP game traffic.
    """

    def __init__(self, port=443, timeout=1.5):
        self.port = port
        self.timeout = timeout

    def ping(self, ip, count=4):

        times = []
        successes = 0

        for _ in range(count):

            start = time.perf_counter()

            try:

                with socket.create_connection(
                    (ip, self.port),
                    timeout=self.timeout
                ):

                    elapsed = (
                        time.perf_counter() - start
                    ) * 1000

                    times.append(elapsed)
                    successes += 1

            except Exception:
                pass

        loss = (
            (count - successes) / count * 100
            if count
            else 100.0
        )

        if not times:

            return {
                "avg": None,
                "min": None,
                "max": None,
                "loss": loss,
            }

        return {
            "avg": statistics.mean(times),
            "min": min(times),
            "max": max(times),
            "loss": loss,
        }
