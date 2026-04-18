from __future__ import annotations

import threading
from contextlib import contextmanager


class Bulkhead:
    def __init__(self, limit: int) -> None:
        self._semaphore = threading.Semaphore(limit)

    @contextmanager
    def slot(self):
        acquired = self._semaphore.acquire(timeout=5)
        if not acquired:
            raise TimeoutError("Bulkhead capacity exhausted")
        try:
            yield
        finally:
            self._semaphore.release()
