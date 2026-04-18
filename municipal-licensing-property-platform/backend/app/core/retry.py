from __future__ import annotations

import random
import threading
import time
from collections import deque
from typing import Callable, TypeVar

T = TypeVar("T")


class RetryBudget:
    def __init__(self, budget_per_minute: int) -> None:
        self.budget_per_minute = budget_per_minute
        self._timestamps: deque[float] = deque()
        self._lock = threading.Lock()

    def consume(self) -> bool:
        now = time.time()
        with self._lock:
            while self._timestamps and now - self._timestamps[0] > 60:
                self._timestamps.popleft()
            if len(self._timestamps) >= self.budget_per_minute:
                return False
            self._timestamps.append(now)
            return True


def retry_with_jitter(
    func: Callable[[], T],
    attempts: int,
    base_delay: float,
    budget: RetryBudget | None = None,
) -> T:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == attempts:
                raise
            if budget and not budget.consume():
                raise RuntimeError("Retry budget exhausted") from exc
            sleep_for = (base_delay * (2 ** (attempt - 1))) + random.uniform(0, base_delay)
            time.sleep(min(sleep_for, 8.0))
    if last_error:
        raise last_error
    raise RuntimeError("retry_with_jitter reached an invalid state")
