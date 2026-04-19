from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import DocumentRecord


class DocumentRepository:
    def list_all(self, db: Session) -> list[DocumentRecord]:
        stmt = select(DocumentRecord).order_by(DocumentRecord.created_at.desc())
        return list(db.scalars(stmt).all())

    def list_for_aggregate(self, db: Session, aggregate_type: str, aggregate_id: str) -> list[DocumentRecord]:
        stmt = (
            select(DocumentRecord)
            .where(
                DocumentRecord.aggregate_type == aggregate_type,
                DocumentRecord.aggregate_id == aggregate_id,
            )
            .order_by(DocumentRecord.created_at.desc())
        )
        return list(db.scalars(stmt).all())

    def list_recent(self, db: Session, limit: int = 20) -> list[DocumentRecord]:
        stmt = select(DocumentRecord).order_by(DocumentRecord.created_at.desc()).limit(limit)
        return list(db.scalars(stmt).all())

    def add(self, db: Session, entity: DocumentRecord) -> DocumentRecord:
        db.add(entity)
        db.flush()
        db.refresh(entity)
        return entity

    def get(self, db: Session, document_id: str) -> DocumentRecord | None:
        return db.get(DocumentRecord, document_id)
