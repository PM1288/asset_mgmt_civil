from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import WorkflowEvent


class WorkflowRepository:
    def list_for_aggregate(self, db: Session, aggregate_type: str, aggregate_id: str) -> list[WorkflowEvent]:
        stmt = (
            select(WorkflowEvent)
            .where(
                WorkflowEvent.aggregate_type == aggregate_type,
                WorkflowEvent.aggregate_id == aggregate_id,
            )
            .order_by(WorkflowEvent.created_at.asc())
        )
        return list(db.scalars(stmt).all())

    def add(self, db: Session, entity: WorkflowEvent) -> WorkflowEvent:
        db.add(entity)
        db.flush()
        db.refresh(entity)
        return entity
