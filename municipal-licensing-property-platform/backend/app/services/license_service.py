from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.encryption import decrypt_value, encrypt_value
from app.core.exceptions import Conflict
from app.db.models import LicenseApplication
from app.db.repositories.licenses import LicenseRepository
from app.db.repositories.properties import PropertyRepository
from app.schemas.license import LicenseAction, LicenseCreate, LicenseOut
from app.services.audit_service import audit_service
from app.services.workflow_service import workflow_service

ALLOWED_TRANSITIONS = {
    "draft": {"submit": "submitted"},
    "submitted": {"review": "under_review"},
    "under_review": {"approve": "approved", "reject": "rejected"},
    "approved": {"revoke": "revoked"},
}


class LicenseService:
    def __init__(self) -> None:
        self.repo = LicenseRepository()
        self.properties = PropertyRepository()

    def _to_schema(self, entity: LicenseApplication) -> LicenseOut:
        return LicenseOut(
            id=entity.id,
            application_number=entity.application_number,
            property_id=entity.property_id,
            license_type=entity.license_type,
            status=entity.status,
            applicant_name=decrypt_value(entity.applicant_name_enc) or "",
            applicant_contact=decrypt_value(entity.applicant_contact_enc),
            current_assignee=entity.current_assignee,
            submitted_at=entity.submitted_at,
            decided_at=entity.decided_at,
            notes=decrypt_value(entity.notes_enc),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def list(self, db: Session) -> list[LicenseOut]:
        return [self._to_schema(entity) for entity in self.repo.list(db)]

    def get(self, db: Session, license_id: str) -> LicenseOut | None:
        entity = self.repo.get(db, license_id)
        return self._to_schema(entity) if entity else None

    def create(self, db: Session, payload: LicenseCreate, actor: str, ip_address: str | None) -> LicenseOut:
        if self.repo.get_by_number(db, payload.application_number):
            raise Conflict("Application number already exists")
        if not self.properties.get(db, payload.property_id):
            raise Conflict("Property does not exist")
        entity = LicenseApplication(
            application_number=payload.application_number,
            property_id=payload.property_id,
            license_type=payload.license_type,
            status="draft",
            applicant_name_enc=encrypt_value(payload.applicant_name) or "",
            applicant_contact_enc=encrypt_value(payload.applicant_contact),
            notes_enc=encrypt_value(payload.notes),
        )
        entity = self.repo.create(db, entity)
        workflow_service.record(
            db,
            aggregate_type="license",
            aggregate_id=entity.id,
            action="create",
            actor_subject=actor,
            from_state=None,
            to_state="draft",
            comments="Application created",
            license_id=entity.id,
        )
        audit_service.record(
            db,
            event_type="license.created",
            outcome="success",
            actor=actor,
            subject=entity.id,
            ip_address=ip_address,
            detail_message=f"Created license application {entity.application_number}",
        )
        return self._to_schema(entity)

    def transition(
        self,
        db: Session,
        *,
        license_id: str,
        transition: str,
        action: LicenseAction,
        actor: str,
        ip_address: str | None,
    ) -> LicenseOut | None:
        entity = self.repo.get(db, license_id)
        if not entity:
            return None
        current = entity.status
        next_state = ALLOWED_TRANSITIONS.get(current, {}).get(transition)
        if not next_state:
            raise Conflict(f"Transition {transition!r} is not valid from state {current!r}")

        entity.status = next_state
        if action.assignee:
            entity.current_assignee = action.assignee
        if transition == "submit":
            entity.submitted_at = datetime.now(timezone.utc)
        if transition in {"approve", "reject", "revoke"}:
            entity.decided_at = datetime.now(timezone.utc)
        if action.comments:
            entity.notes_enc = encrypt_value(action.comments)

        db.add(entity)
        db.flush()
        db.refresh(entity)

        workflow_service.record(
            db,
            aggregate_type="license",
            aggregate_id=entity.id,
            action=transition,
            actor_subject=actor,
            from_state=current,
            to_state=next_state,
            comments=action.comments,
            license_id=entity.id,
        )
        audit_service.record(
            db,
            event_type=f"license.{transition}",
            outcome="success",
            actor=actor,
            subject=entity.id,
            ip_address=ip_address,
            detail_message=f"Transitioned license {entity.application_number} to {next_state}",
        )
        return self._to_schema(entity)


license_service = LicenseService()
