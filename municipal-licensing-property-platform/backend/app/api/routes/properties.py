from __future__ import annotations

from fastapi import APIRouter, Depends, File, Header, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.idempotency import idempotency_service, payload_hash
from app.core.security import SubjectContext, require_roles
from app.db.session import get_db
from app.schemas.document import DocumentOut
from app.schemas.property import PropertyCreate, PropertyOut, PropertyUpdate
from app.services.document_service import document_service
from app.services.property_service import property_service

router = APIRouter(prefix="/properties", tags=["properties"])
settings = get_settings()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.get("", response_model=list[PropertyOut])
def list_properties(
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "auditor", "viewer")
    ),
):
    return property_service.list(db)


@router.get("/{property_id}", response_model=PropertyOut)
def get_property(
    property_id: str,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "auditor", "viewer")
    ),
):
    entity = property_service.get(db, property_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Property not found")
    return entity


@router.post("", response_model=PropertyOut, status_code=status.HTTP_201_CREATED)
def create_property(
    payload: PropertyCreate,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "property-officer")),
):
    request_hash = payload_hash(payload.model_dump())
    if idempotency_key:
        cached = idempotency_service.check(db, key=idempotency_key, route="POST:/properties", request_hash=request_hash)
        if cached:
            code, body = cached
            return JSONResponse(status_code=code, content=body)

    result = property_service.create(
        db,
        payload=payload,
        actor=subject.subject,
        ip_address=_client_ip(request),
    )
    db.commit()
    body = result.model_dump(mode="json")
    if idempotency_key:
        idempotency_service.store(
            db,
            key=idempotency_key,
            route="POST:/properties",
            request_hash=request_hash,
            status_code=201,
            body=body,
        )
        db.commit()
    return result


@router.put("/{property_id}", response_model=PropertyOut)
def update_property(
    property_id: str,
    payload: PropertyUpdate,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "property-officer")),
):
    request_hash = payload_hash(payload.model_dump(exclude_none=True))
    if idempotency_key:
        cached = idempotency_service.check(
            db, key=idempotency_key, route=f"PUT:/properties/{property_id}", request_hash=request_hash
        )
        if cached:
            code, body = cached
            return JSONResponse(status_code=code, content=body)

    result = property_service.update(
        db,
        property_id=property_id,
        payload=payload,
        actor=subject.subject,
        ip_address=_client_ip(request),
    )
    if not result:
        raise HTTPException(status_code=404, detail="Property not found")
    db.commit()
    body = result.model_dump(mode="json")
    if idempotency_key:
        idempotency_service.store(
            db,
            key=idempotency_key,
            route=f"PUT:/properties/{property_id}",
            request_hash=request_hash,
            status_code=200,
            body=body,
        )
        db.commit()
    return result


@router.get("/{property_id}/documents", response_model=list[DocumentOut])
def list_property_documents(
    property_id: str,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "auditor", "viewer")
    ),
):
    return document_service.list(db, aggregate_type="property", aggregate_id=property_id)


@router.post("/{property_id}/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_property_document(
    property_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "property-officer")),
):
    payload = await file.read()
    if len(payload) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    if file.content_type not in settings.allowed_file_types:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    if not property_service.get(db, property_id):
        raise HTTPException(status_code=404, detail="Property not found")
    result = document_service.upload(
        db,
        aggregate_type="property",
        aggregate_id=property_id,
        property_id=property_id,
        license_id=None,
        filename=file.filename or "upload.bin",
        media_type=file.content_type or "application/octet-stream",
        payload=payload,
        actor=subject.subject,
        ip_address=_client_ip(request),
    )
    db.commit()
    return result
