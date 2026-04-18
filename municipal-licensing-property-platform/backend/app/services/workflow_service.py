from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.encryption import decrypt_value, encrypt_value
from app.db.models import WorkflowEvent
from app.db.repositories.workflows import WorkflowRepository
from app.schemas.workflow import WorkflowEventOut


class WorkflowService:
    def __init__(self) -> None:
        self.repo = WorkflowRepository()

    def record(
        self,
        db: Session,
        *,
        aggregate_type: str,
        aggregate_id: str,
        action: str,
        actor_subject: str,
        from_state: str | None,
        to_state: str | None,
        comments: str | None = None,
        license_id: str | None = None,
    ) -> WorkflowEvent:
        entity = WorkflowEvent(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            action=action,
            actor_subject=actor_subject,
            from_state=from_state,
            to_state=to_state,
            comments_enc=encrypt_value(comments),
            license_id=license_id,
        )
        return self.repo.add(db, entity)

    def list(self, db: Session, aggregate_type: str, aggregate_id: str) -> list[WorkflowEventOut]:
        items = self.repo.list_for_aggregate(db, aggregate_type, aggregate_id)
        return [
            WorkflowEventOut(
                id=item.id,
                aggregate_type=item.aggregate_type,
                aggregate_id=item.aggregate_id,
                action=item.action,
                from_state=item.from_state,
                to_state=item.to_state,
                actor_subject=item.actor_subject,
                comments=decrypt_value(item.comments_enc),
                created_at=item.created_at,
            )
            for item in items
        ]


workflow_service = WorkflowService()
