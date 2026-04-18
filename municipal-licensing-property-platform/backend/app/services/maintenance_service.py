from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import AuditEvent, IdempotencyRecord
from app.services.audit_service import audit_service


class MaintenanceService:
    def cleanup(self, db: Session, actor: str, ip_address: str | None) -> dict[str, int]:
        settings = get_settings()
        now = datetime.now(timezone.utc)

        stale_idempotency = now - timedelta(days=settings.idempotency_retention_days)
        stale_audit = now - timedelta(days=settings.audit_retention_days)

        idempotency_deleted = db.execute(
            delete(IdempotencyRecord).where(IdempotencyRecord.created_at < stale_idempotency)
        ).rowcount or 0
        audit_deleted = db.execute(
            delete(AuditEvent).where(AuditEvent.created_at < stale_audit)
        ).rowcount or 0

        audit_service.record(
            db,
            event_type="maintenance.cleanup",
            outcome="success",
            actor=actor,
            subject="maintenance",
            ip_address=ip_address,
            detail_message="Executed retention cleanup",
            details_json={"idempotency_deleted": idempotency_deleted, "audit_deleted": audit_deleted},
        )
        return {"idempotency_deleted": idempotency_deleted, "audit_deleted": audit_deleted}


maintenance_service = MaintenanceService()
