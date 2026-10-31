from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable


class SlidingWindowLimiter:
    """Per-process sliding-window limit by client key.

    State lives in this process only: each worker enforces its own limit, so N workers
    allow up to N times the configured rate. Use a gateway or shared store for a global limit.
    """

    def __init__(
        self,
        limit: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
        max_clients: int = 10_000,
    ) -> None:
        self.limit = limit
        self.window = window_seconds
        self.clock = clock
        self.max_clients = max_clients
        self._hits: dict[str, deque[float]] = {}

    @property
    def tracked_clients(self) -> int:
        return len(self._hits)

    def check(self, key: str) -> float | None:
        """Record a request. Return None if allowed, else seconds until one is allowed."""
        now = self.clock()
        if key not in self._hits and len(self._hits) >= self.max_clients:
            self._purge(now)
            if len(self._hits) >= self.max_clients:
                return self.window
        hits = self._hits.setdefault(key, deque())
        while hits and now - hits[0] >= self.window:
            hits.popleft()
        if len(hits) >= self.limit:
            return self.window - (now - hits[0])
        hits.append(now)
        return None

    def _purge(self, now: float) -> None:
        for key in [
            k for k, hits in self._hits.items() if not hits or now - hits[-1] >= self.window
        ]:
            del self._hits[key]
