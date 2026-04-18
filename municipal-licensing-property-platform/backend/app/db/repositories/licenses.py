from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import LicenseApplication


class LicenseRepository:
    def list(self, db: Session) -> list[LicenseApplication]:
        return list(db.scalars(select(LicenseApplication).order_by(LicenseApplication.created_at.desc())).all())

    def get(self, db: Session, license_id: str) -> LicenseApplication | None:
        return db.get(LicenseApplication, license_id)

    def get_by_number(self, db: Session, application_number: str) -> LicenseApplication | None:
        return db.scalar(
            select(LicenseApplication).where(
                LicenseApplication.application_number == application_number
            )
        )

    def create(self, db: Session, entity: LicenseApplication) -> LicenseApplication:
        db.add(entity)
        db.flush()
        db.refresh(entity)
        return entity
