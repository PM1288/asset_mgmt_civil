from __future__ import annotations

import threading
import time
from dataclasses import dataclass


@dataclass
class CircuitState:
    failures: int = 0
    opened_at: float | None = None


class CircuitBreaker:
    def __init__(self, failure_threshold: int, reset_seconds: int) -> None:
        self.failure_threshold = failure_threshold
        self.reset_seconds = reset_seconds
        self._state = CircuitState()
        self._lock = threading.Lock()

    def allow(self) -> bool:
        with self._lock:
            if self._state.opened_at is None:
                return True
            if time.time() - self._state.opened_at >= self.reset_seconds:
                self._state.failures = 0
                self._state.opened_at = None
                return True
            return False

    def record_success(self) -> None:
        with self._lock:
            self._state.failures = 0
            self._state.opened_at = None

    def record_failure(self) -> None:
        with self._lock:
            self._state.failures += 1
            if self._state.failures >= self.failure_threshold:
                self._state.opened_at = time.time()

    @property
    def is_open(self) -> bool:
        return not self.allow()
