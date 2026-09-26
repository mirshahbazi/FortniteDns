import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from .constants import (
    FAST_QUERIES,
    FAST_QUERY_COUNT,
    FORTNITE_ENDPOINTS,
    FORTNITE_PING_COUNT,
    FORTNITE_REGIONS,
    MAX_FORTNITE_WORKERS,
    MAX_WORKERS,
)


def _run_parallel(fn, items, max_workers, progress_cb, cancel_flag, error_result):
    """
    Shared concurrency runner for both testers below. Runs `fn` on
    each item in a thread pool, reporting (completed, total,
    results-so-far) after every completion, and stops early —
    cancelling any not-yet-started work — once `cancel_flag()`
    returns True.

    This is the piece that used to be duplicated (and, for the
    Fortnite test, missing entirely — it ran one candidate at a
    time) inside the Tkinter App class. Having it here means the
    concurrency behavior can be unit tested with a fake `fn` and no
    UI at all.
    """

    total = len(items)
    completed = 0
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:

        futures = {
            executor.submit(fn, item): item
            for item in items
        }

        for future in as_completed(futures):

            if cancel_flag and cancel_flag():

                executor.shutdown(
                    wait=False,
                    cancel_futures=True
                )

                break

            item = futures[future]

            try:
                results.append(future.result())
            except Exception:
                results.append(error_result(item))

            completed += 1

            if progress_cb:
                progress_cb(completed, total, list(results))

    return results


class FastDnsTester:
    """
    "Fast Test": resolves a handful of well-known domains through
    each candidate DNS server and measures resolution latency and
    success rate. This is the cheap first pass used to narrow down
    a long DNS list before the much more expensive Fortnite test.
    """

    def __init__(
        self,
        resolver,
        queries=None,
        query_count=FAST_QUERY_COUNT,
        max_workers=MAX_WORKERS
    ):
        self.resolver = resolver
        self.queries = list(queries) if queries is not None else list(FAST_QUERIES)
        self.query_count = query_count
        self.max_workers = max_workers

    def test_one(self, record):

        name, primary, secondary = record

        times = []
        success = 0

        for domain in self.queries:

            for _ in range(self.query_count):

                ips, elapsed = self.resolver.resolve(
                    domain,
                    primary
                )

                if ips:
                    success += 1
                    times.append(elapsed)

        total = len(self.queries) * self.query_count

        success_rate = (
            success / total * 100
            if total
            else 0
        )

        avg = statistics.mean(times) if times else None
        minimum = min(times) if times else None

        return {
            "name": name,
            "primary": primary,
            "secondary": secondary,
            "avg": avg,
            "min": minimum,
            "success": success_rate,
            "queries": success,
            "total": total,
        }

    @staticmethod
    def _error_result(record):

        name, primary, secondary = record

        return {
            "name": name,
            "primary": primary,
            "secondary": secondary,
            "avg": None,
            "min": None,
            "success": 0,
            "queries": 0,
            "total": 0
        }

    def test_many(self, records, progress_cb=None, cancel_flag=None):

        results = _run_parallel(
            self.test_one,
            records,
            self.max_workers,
            progress_cb,
            cancel_flag,
            self._error_result
        )

        # Best DNS resolution first: highest success rate, then
        # lowest average latency.
        results.sort(
            key=lambda x: (
                -x["success"],
                x["avg"] if x["avg"] is not None else 999999
            )
        )

        return results


class FortniteDnsTester:
    """
    "Fortnite Test": for each DNS candidate, resolves every Epic
    region endpoint through it and pings the resulting IP, then
    scores the candidate on average latency/loss/jitter. Candidates
    are tested concurrently (bounded by max_workers) — sequential
    testing was the cause of the multi-minute "hang" this used to
    have with a full candidate list.
    """

    def __init__(
        self,
        resolver,
        pinger,
        regions=None,
        endpoints=None,
        ping_count=FORTNITE_PING_COUNT,
        max_workers=MAX_FORTNITE_WORKERS
    ):
        self.resolver = resolver
        self.pinger = pinger
        self.regions = list(regions) if regions is not None else list(FORTNITE_REGIONS)
        self.endpoints = dict(endpoints) if endpoints is not None else dict(FORTNITE_ENDPOINTS)
        self.ping_count = ping_count
        self.max_workers = max_workers

    def test_one(self, dns_result):

        primary = dns_result["primary"]

        region_results = []

        for region in self.regions:

            hostname = self.endpoints[region]

            ips, dns_time = self.resolver.resolve(
                hostname,
                primary
            )

            if not ips:

                region_results.append({
                    "region": region,
                    "avg": None,
                    "loss": 100,
                    "jitter": None,
                    "ip": None,
                    "dns_time": dns_time
                })

                continue

            best_ping = None

            # Try at most 2 resolved IPs, stopping at the first one
            # that actually responds, instead of racing several IPs
            # against each other to find the theoretical best one —
            # that's what made this test slow.
            for ip in ips[:2]:

                ping = self.pinger.ping(
                    ip,
                    self.ping_count
                )

                if ping["avg"] is None:
                    continue

                best_ping = ping
                best_ping["ip"] = ip

                break

            if best_ping is None:

                region_results.append({
                    "region": region,
                    "avg": None,
                    "loss": 100,
                    "jitter": None,
                    "ip": ips[0],
                    "dns_time": dns_time
                })

            else:

                region_results.append({
                    "region": region,
                    "avg": best_ping["avg"],
                    "loss": best_ping["loss"],
                    "jitter": best_ping["jitter"],
                    "ip": best_ping["ip"],
                    "dns_time": dns_time
                })

        valid = [
            x for x in region_results
            if x["avg"] is not None
        ]

        if not valid:

            score = float("inf")

        else:

            avg_ping = statistics.mean(x["avg"] for x in valid)
            avg_loss = statistics.mean(x["loss"] for x in valid)

            jitters = [
                x["jitter"] for x in valid
                if x["jitter"] is not None
            ]

            avg_jitter = statistics.mean(jitters) if jitters else 0

            unreachable = len(region_results) - len(valid)

            score = (
                avg_ping
                + avg_loss * 12
                + avg_jitter * 0.5
                + unreachable * 100
            )

        return {
            **dns_result,
            "fortnite": region_results,
            "score": score
        }

    @staticmethod
    def _error_result(candidate):

        return {
            **candidate,
            "fortnite": [],
            "score": float("inf")
        }

    def test_many(self, candidates, progress_cb=None, cancel_flag=None):

        results = _run_parallel(
            self.test_one,
            candidates,
            self.max_workers,
            progress_cb,
            cancel_flag,
            self._error_result
        )

        results.sort(key=lambda x: x["score"])

        return results
