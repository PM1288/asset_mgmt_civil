from __future__ import annotations

import shutil

import redis
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import jwks_cache
from app.schemas.health import ComponentHealth, HealthEnvelope


class HealthService:
    def live(self) -> HealthEnvelope:
        return HealthEnvelope(
            status="ok",
            components=[ComponentHealth(name="api", ok=True, detail="process alive")],
        )

    def readiness(self, db: Session) -> HealthEnvelope:
        settings = get_settings()
        components: list[ComponentHealth] = []

        try:
            db.execute(text("select 1"))
            components.append(ComponentHealth(name="database", ok=True, detail="query ok"))
        except SQLAlchemyError as exc:
            components.append(ComponentHealth(name="database", ok=False, detail=str(exc)))

        try:
            client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
            client.ping()
            components.append(ComponentHealth(name="redis", ok=True, detail="ping ok"))
        except Exception as exc:  # noqa: BLE001
            components.append(ComponentHealth(name="redis", ok=False, detail=str(exc)))

        try:
            jwks = jwks_cache.get()
            count = len(jwks.get("keys", []))
            components.append(ComponentHealth(name="auth", ok=True, detail=f"jwks={count}"))
        except Exception as exc:  # noqa: BLE001
            components.append(ComponentHealth(name="auth", ok=False, detail=str(exc)))

        usage = shutil.disk_usage(settings.docs_root)
        free_mb = usage.free // (1024 * 1024)
        disk_ok = free_mb >= settings.minimum_free_disk_mb
        components.append(
            ComponentHealth(name="document-store", ok=disk_ok, detail=f"free_mb={free_mb}")
        )

        status = "ok" if all(item.ok for item in components) else "degraded"
        return HealthEnvelope(status=status, components=components)

    def startup(self) -> HealthEnvelope:
        settings = get_settings()
        components = [
            ComponentHealth(name="config", ok=True, detail=settings.environment),
            ComponentHealth(name="logs-root", ok=settings.logs_root.exists(), detail=str(settings.logs_root)),
            ComponentHealth(name="docs-root", ok=settings.docs_root.exists(), detail=str(settings.docs_root)),
            ComponentHealth(name="backups-root", ok=settings.backups_root.exists(), detail=str(settings.backups_root)),
        ]
        status = "ok" if all(item.ok for item in components) else "degraded"
        return HealthEnvelope(status=status, components=components)


health_service = HealthService()
