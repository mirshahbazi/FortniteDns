import re
import statistics

from .utils import run_command


class WindowsPinger:
    """
    Wraps the Windows `ping` command and parses its output. Split
    out from the Fortnite tester so the ping strategy (currently:
    real ICMP via subprocess) can be swapped or mocked independently
    of the region/scoring logic.
    """

    def __init__(self, timeout_ms=1000):
        self.timeout_ms = timeout_ms

    def ping(self, ip, count=5):

        command = [
            "ping",
            "-n",
            str(count),
            "-w",
            str(self.timeout_ms),
            ip
        ]

        code, stdout, stderr = run_command(
            command,
            timeout=count * 2 + 4
        )

        if not stdout:

            return {
                "avg": None,
                "min": None,
                "max": None,
                "loss": 100.0,
                "jitter": None
            }

        times = []

        for line in stdout.splitlines():

            match = re.search(
                r"time[=<]\s*(\d+(?:\.\d+)?)\s*ms",
                line,
                re.IGNORECASE
            )

            if match:

                try:
                    times.append(
                        float(
                            match.group(1)
                        )
                    )
                except Exception:
                    pass

        loss = 100.0

        match = re.search(
            r"\((\d+(?:\.\d+)?)%\s*loss\)",
            stdout,
            re.IGNORECASE
        )

        if match:

            try:
                loss = float(
                    match.group(1)
                )
            except Exception:
                pass

        if not times:

            return {
                "avg": None,
                "min": None,
                "max": None,
                "loss": loss,
                "jitter": None
            }

        avg = statistics.mean(times)

        minimum = min(times)

        maximum = max(times)

        if len(times) > 1:

            jitter_values = [
                abs(
                    times[i]
                    - times[i - 1]
                )
                for i in range(
                    1,
                    len(times)
                )
            ]

            jitter = statistics.mean(
                jitter_values
            )

        else:

            jitter = 0

        return {
            "avg": avg,
            "min": minimum,
            "max": maximum,
            "loss": loss,
            "jitter": jitter
        }
