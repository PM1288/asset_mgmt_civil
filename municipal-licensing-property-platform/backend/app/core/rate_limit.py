from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict

import redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self) -> None:
        self._fallback: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def _redis_client(self):
        settings = get_settings()
        return redis.Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=settings.outbound_connect_timeout_seconds,
            socket_timeout=settings.outbound_read_timeout_seconds,
            health_check_interval=30,
            decode_responses=True,
        )

    def allow(self, key: str) -> bool:
        settings = get_settings()
        window = 60
        try:
            client = self._redis_client()
            redis_key = f"ratelimit:{key}:{int(time.time() // window)}"
            current = client.incr(redis_key)
            if current == 1:
                client.expire(redis_key, window + settings.failed_request_penalty_seconds)
            return current <= settings.rate_limit_per_minute + settings.rate_limit_burst
        except Exception as exc:  # noqa: BLE001
            logger.warning("redis rate-limit fallback activated: %s", exc)
            now = time.time()
            with self._lock:
                events = [t for t in self._fallback[key] if now - t < window]
                if len(events) >= settings.rate_limit_per_minute + settings.rate_limit_burst:
                    self._fallback[key] = events
                    return False
                events.append(now)
                self._fallback[key] = events
                return True


rate_limiter = RateLimiter()
