from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import DocumentRecord
from app.db.repositories.documents import DocumentRepository
from app.schemas.document import DocumentOut
from app.storage.local_fs import document_store
from app.services.audit_service import audit_service


class DocumentService:
    def __init__(self) -> None:
        self.repo = DocumentRepository()

    def get(self, db: Session, document_id: str) -> DocumentOut | None:
        entity = self.repo.get(db, document_id)
        return DocumentOut.model_validate(entity) if entity else None

    def list(self, db: Session, aggregate_type: str, aggregate_id: str) -> list[DocumentOut]:
        items = self.repo.list_for_aggregate(db, aggregate_type, aggregate_id)
        return [DocumentOut.model_validate(item) for item in items]

    def upload(
        self,
        db: Session,
        *,
        aggregate_type: str,
        aggregate_id: str,
        property_id: str | None,
        license_id: str | None,
        filename: str,
        media_type: str,
        payload: bytes,
        actor: str,
        ip_address: str | None,
    ) -> DocumentOut:
        relative_path, checksum, size = document_store.save(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            filename=filename,
            payload=payload,
        )
        entity = DocumentRecord(
            aggregate_type=aggregate_type,
            aggregate_id=aggregate_id,
            property_id=property_id,
            license_id=license_id,
            storage_path=relative_path,
            original_filename=filename,
            media_type=media_type,
            sha256=checksum,
            size_bytes=size,
            uploaded_by=actor,
        )
        entity = self.repo.add(db, entity)
        audit_service.record(
            db,
            event_type="document.uploaded",
            outcome="success",
            actor=actor,
            subject=entity.id,
            ip_address=ip_address,
            detail_message=f"Uploaded {filename} for {aggregate_type}:{aggregate_id}",
        )
        return DocumentOut.model_validate(entity)


document_service = DocumentService()
