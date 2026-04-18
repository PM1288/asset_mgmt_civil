from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any

import httpx
import jwt
from fastapi import Depends, Header
from jwt import InvalidTokenError

from app.core.bulkhead import Bulkhead
from app.core.circuit_breaker import CircuitBreaker
from app.core.config import get_settings
from app.core.exceptions import Forbidden, ServiceUnavailable
from app.core.retry import RetryBudget, retry_with_jitter

logger = logging.getLogger(__name__)


@dataclass
class SubjectContext:
    subject: str
    username: str
    email: str | None
    roles: set[str]
    token: dict[str, Any]


class JWKSCache:
    def __init__(self) -> None:
        settings = get_settings()
        self._jwks: dict[str, Any] | None = None
        self._last_loaded: float = 0
        self._lock = threading.Lock()
        self._breaker = CircuitBreaker(
            failure_threshold=settings.circuit_breaker_failure_threshold,
            reset_seconds=settings.circuit_breaker_reset_seconds,
        )
        self._budget = RetryBudget(settings.retry_budget_per_minute)
        self._bulkhead = Bulkhead(settings.auth_bulkhead_limit)

    def _fetch_jwks(self) -> dict[str, Any]:
        settings = get_settings()
        timeout = httpx.Timeout(
            connect=settings.outbound_connect_timeout_seconds,
            read=settings.outbound_read_timeout_seconds,
            write=settings.outbound_read_timeout_seconds,
            pool=settings.outbound_connect_timeout_seconds,
        )

        def call() -> dict[str, Any]:
            if not self._breaker.allow():
                raise RuntimeError("JWKS circuit breaker open")
            with self._bulkhead.slot():
                with httpx.Client(timeout=timeout, verify=settings.keycloak_verify_tls) as client:
                    response = client.get(settings.keycloak_jwks_url)
                    response.raise_for_status()
                    data = response.json()
                    self._breaker.record_success()
                    return data

        try:
            return retry_with_jitter(
                func=call,
                attempts=settings.retry_max_attempts,
                base_delay=settings.retry_backoff_base_seconds,
                budget=self._budget,
            )
        except Exception as exc:  # noqa: BLE001
            self._breaker.record_failure()
            raise RuntimeError("Unable to refresh JWKS") from exc

    def get(self) -> dict[str, Any]:
        settings = get_settings()
        with self._lock:
            now = time.time()
            if self._jwks and now - self._last_loaded < settings.keycloak_jwks_cache_ttl_seconds:
                return self._jwks
            self._jwks = self._fetch_jwks()
            self._last_loaded = now
            return self._jwks


jwks_cache = JWKSCache()


def _kid_to_key(kid: str, jwks: dict[str, Any]) -> Any:
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)
    raise KeyError(f"Unable to locate kid {kid}")


def decode_token(bearer_token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        header = jwt.get_unverified_header(bearer_token)
        kid = header["kid"]
        jwks = jwks_cache.get()
        signing_key = _kid_to_key(kid, jwks)
        return jwt.decode(
            bearer_token,
            signing_key,
            algorithms=["RS256", "RS384", "RS512"],
            issuer=str(settings.keycloak_issuer_url).rstrip("/"),
            options={"verify_aud": False},
        )
    except InvalidTokenError as exc:
        logger.warning("token validation failed: %s", exc)
        raise Forbidden("Invalid bearer token") from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("token verification unavailable")
        raise ServiceUnavailable("Authentication subsystem unavailable") from exc


def build_subject_context(token_data: dict[str, Any]) -> SubjectContext:
    realm_roles = set(token_data.get("realm_access", {}).get("roles", []))
    resource_roles: set[str] = set()
    for _, details in token_data.get("resource_access", {}).items():
        resource_roles.update(details.get("roles", []))

    roles = realm_roles | resource_roles
    return SubjectContext(
        subject=token_data.get("sub", "unknown"),
        username=token_data.get("preferred_username")
        or token_data.get("email")
        or token_data.get("sub", "unknown"),
        email=token_data.get("email"),
        roles=roles,
        token=token_data,
    )


def auth_subject(authorization: str = Header(default="")) -> SubjectContext:
    if not authorization.startswith("Bearer "):
        raise Forbidden("Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    return build_subject_context(decode_token(token))


def require_roles(*required: str):
    def inner(subject: SubjectContext = Depends(auth_subject)) -> SubjectContext:
        if required and not (subject.roles & set(required)):
            raise Forbidden()
        return subject

    return inner
