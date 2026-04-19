from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.encryption import decrypt_value, encrypt_value
from app.core.exceptions import Conflict
from app.db.models import Property
from app.db.repositories.properties import PropertyRepository
from app.schemas.property import PropertyCreate, PropertyOut, PropertyUpdate
from app.services.audit_service import audit_service
from app.services.workflow_service import workflow_service


class PropertyService:
    def __init__(self) -> None:
        self.repo = PropertyRepository()

    def _to_schema(self, entity: Property) -> PropertyOut:
        return PropertyOut(
            id=entity.id,
            property_number=entity.property_number,
            ward_code=entity.ward_code,
            address_line_1=entity.address_line_1,
            address_line_2=entity.address_line_2,
            city=entity.city,
            district=entity.district,
            state=entity.state,
            postal_code=entity.postal_code,
            geo_lat=entity.geo_lat,
            geo_lng=entity.geo_lng,
            status=entity.status,
            use_type=entity.use_type,
            owner_name=decrypt_value(entity.owner_name_enc) or "",
            owner_contact=decrypt_value(entity.owner_contact_enc),
            assessment_zone=entity.assessment_zone,
            remarks=decrypt_value(entity.remarks_enc),
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def list(self, db: Session) -> list[PropertyOut]:
        return [self._to_schema(entity) for entity in self.repo.list(db)]

    def get(self, db: Session, property_id: str) -> PropertyOut | None:
        entity = self.repo.get(db, property_id)
        return self._to_schema(entity) if entity else None

    def create(self, db: Session, payload: PropertyCreate, actor: str, ip_address: str | None) -> PropertyOut:
        if self.repo.get_by_number(db, payload.property_number):
            raise Conflict("Property number already exists")
        entity = Property(
            property_number=payload.property_number,
            ward_code=payload.ward_code,
            address_line_1=payload.address_line_1,
            address_line_2=payload.address_line_2,
            city=payload.city,
            district=payload.district,
            state=payload.state,
            postal_code=payload.postal_code,
            geo_lat=payload.geo_lat,
            geo_lng=payload.geo_lng,
            status=payload.status,
            use_type=payload.use_type,
            owner_name_enc=encrypt_value(payload.owner_name) or "",
            owner_contact_enc=encrypt_value(payload.owner_contact),
            assessment_zone=payload.assessment_zone,
            remarks_enc=encrypt_value(payload.remarks),
        )
        entity = self.repo.create(db, entity)
        workflow_service.record(
            db,
            aggregate_type="property",
            aggregate_id=entity.id,
            action="create",
            actor_subject=actor,
            from_state=None,
            to_state=entity.status,
            comments="Property created",
            license_id=None,
        )
        audit_service.record(
            db,
            event_type="property.created",
            outcome="success",
            actor=actor,
            subject=entity.id,
            ip_address=ip_address,
            detail_message=f"Created property {entity.property_number}",
        )
        return self._to_schema(entity)

    def update(
        self,
        db: Session,
        property_id: str,
        payload: PropertyUpdate,
        actor: str,
        ip_address: str | None,
    ) -> PropertyOut | None:
        entity = self.repo.get(db, property_id)
        if not entity:
            return None
        for field in [
            "ward_code",
            "address_line_1",
            "address_line_2",
            "city",
            "district",
            "state",
            "postal_code",
            "geo_lat",
            "geo_lng",
            "status",
            "use_type",
            "assessment_zone",
        ]:
            value = getattr(payload, field)
            if value is not None:
                setattr(entity, field, value)

        if payload.owner_name is not None:
            entity.owner_name_enc = encrypt_value(payload.owner_name) or ""
        if payload.owner_contact is not None:
            entity.owner_contact_enc = encrypt_value(payload.owner_contact)
        if payload.remarks is not None:
            entity.remarks_enc = encrypt_value(payload.remarks)

        db.add(entity)
        db.flush()
        db.refresh(entity)
        workflow_service.record(
            db,
            aggregate_type="property",
            aggregate_id=entity.id,
            action="update",
            actor_subject=actor,
            from_state=None,
            to_state=entity.status,
            comments="Property details updated",
            license_id=None,
        )
        audit_service.record(
            db,
            event_type="property.updated",
            outcome="success",
            actor=actor,
            subject=entity.id,
            ip_address=ip_address,
            detail_message=f"Updated property {entity.property_number}",
        )
        return self._to_schema(entity)


property_service = PropertyService()
