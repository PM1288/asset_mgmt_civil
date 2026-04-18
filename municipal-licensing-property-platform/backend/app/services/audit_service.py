from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.orm import Session

from app.db.models import AuditEvent
from app.db.repositories.audits import AuditRepository

audit_logger = logging.getLogger("audit")


class AuditService:
    def __init__(self) -> None:
        self.repo = AuditRepository()

    def record(
        self,
        db: Session,
        *,
        event_type: str,
        outcome: str,
        actor: str | None = None,
        subject: str | None = None,
        ip_address: str | None = None,
        detail_message: str | None = None,
        details_json: dict[str, Any] | None = None,
    ) -> AuditEvent:
        entity = AuditEvent(
            event_type=event_type,
            outcome=outcome,
            actor=actor,
            subject=subject,
            ip_address=ip_address,
            detail_message=detail_message,
            details_json=details_json or {},
        )
        entity = self.repo.add(db, entity)
        audit_logger.info(
            detail_message or event_type,
            extra={"subject": subject or "system"},
        )
        return entity


audit_service = AuditService()
