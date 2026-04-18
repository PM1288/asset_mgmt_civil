from __future__ import annotations

import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.rate_limit import rate_limiter
from app.telemetry.metrics import REQUEST_LATENCY_SECONDS, REQUESTS_TOTAL

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        started = time.perf_counter()

        key = f"{request.client.host if request.client else 'unknown'}:{request.url.path}"
        if not rate_limiter.allow(key):
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests", "request_id": request_id},
                headers={"X-Request-ID": request_id, "Retry-After": "60"},
            )

        try:
            response = await call_next(request)
        except Exception:  # noqa: BLE001
            elapsed = time.perf_counter() - started
            REQUESTS_TOTAL.labels(
                method=request.method, path=request.url.path, status="500"
            ).inc()
            REQUEST_LATENCY_SECONDS.labels(method=request.method, path=request.url.path).observe(
                elapsed
            )
            logger.exception("unhandled exception", extra={"request_id": request_id})
            raise

        elapsed = time.perf_counter() - started
        REQUESTS_TOTAL.labels(
            method=request.method, path=request.url.path, status=str(response.status_code)
        ).inc()
        REQUEST_LATENCY_SECONDS.labels(method=request.method, path=request.url.path).observe(
            elapsed
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=()"
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Robots-Tag"] = "noindex, nofollow"
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
