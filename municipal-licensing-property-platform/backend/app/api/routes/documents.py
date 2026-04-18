from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import SubjectContext, require_roles
from app.db.session import get_db
from app.services.document_service import document_service
from app.storage.local_fs import document_store

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("/{document_id}/download")
def download_document(
    document_id: str,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "licensing-officer", "auditor", "viewer")
    ),
):
    document = document_service.get(db, document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    if not document_store.exists(document.storage_path):
        raise HTTPException(status_code=404, detail="Backing file missing")

    payload = document_store.read(document.storage_path)

    def iterator():
        yield payload

    return StreamingResponse(
        iterator(),
        media_type=document.media_type,
        headers={"Content-Disposition": f'attachment; filename="{document.original_filename}"'},
    )
