from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AuditEvent


class AuditRepository:
    def list_recent(self, db: Session, limit: int = 100) -> list[AuditEvent]:
        stmt = select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(limit)
        return list(db.scalars(stmt).all())

    def add(self, db: Session, entity: AuditEvent) -> AuditEvent:
        db.add(entity)
        db.flush()
        db.refresh(entity)
        return entity
