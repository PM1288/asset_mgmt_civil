from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Property


class PropertyRepository:
    def list(self, db: Session) -> list[Property]:
        return list(db.scalars(select(Property).order_by(Property.created_at.desc())).all())

    def get(self, db: Session, property_id: str) -> Property | None:
        return db.get(Property, property_id)

    def get_by_number(self, db: Session, property_number: str) -> Property | None:
        return db.scalar(select(Property).where(Property.property_number == property_number))

    def create(self, db: Session, entity: Property) -> Property:
        db.add(entity)
        db.flush()
        db.refresh(entity)
        return entity
