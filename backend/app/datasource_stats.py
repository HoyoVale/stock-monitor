"""Data source call statistics tracker.

Tracks success/failure counts and average response time per datasource.
Exposed via a module-level singleton.
"""

import time
from collections import defaultdict
from contextlib import contextmanager
from typing import Optional


class DatasourceStats:
    """Thread-safe-ish stats collector (single event loop → no locks needed)."""

    def __init__(self):
        self._calls: dict[str, int] = defaultdict(int)
        self._failures: dict[str, int] = defaultdict(int)
        self._total_ms: dict[str, float] = defaultdict(float)

    @contextmanager
    def track(self, datasource: str):
        """Context manager: track a datasource call.

        Usage:
            with stats.track("akshare"):
                data = await ak.func()
        """
        start = time.perf_counter()
        try:
            yield
            elapsed = (time.perf_counter() - start) * 1000
            self._calls[datasource] += 1
            self._total_ms[datasource] += elapsed
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            self._calls[datasource] += 1
            self._failures[datasource] += 1
            self._total_ms[datasource] += elapsed
            raise

    def snapshot(self) -> dict:
        """Return a dict snapshot of current stats."""
        sources = set(self._calls.keys()) | set(self._failures.keys())
        result = {}
        for ds in sorted(sources):
            calls = self._calls[ds]
            failures = self._failures[ds]
            total_ms = self._total_ms[ds]
            result[ds] = {
                "calls": calls,
                "failures": failures,
                "success_rate": round((calls - failures) / calls * 100, 1) if calls else 0,
                "avg_ms": round(total_ms / calls, 1) if calls else 0,
            }
        return result

    def reset(self):
        self._calls.clear()
        self._failures.clear()
        self._total_ms.clear()


# Singleton
stats = DatasourceStats()
