from __future__ import annotations

from fastapi import APIRouter, Depends, File, Header, HTTPException, Request, UploadFile, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.idempotency import idempotency_service, payload_hash
from app.core.security import SubjectContext, require_roles
from app.db.session import get_db
from app.schemas.document import DocumentOut
from app.schemas.license import LicenseAction, LicenseCreate, LicenseOut
from app.services.document_service import document_service
from app.services.license_service import license_service

router = APIRouter(prefix="/licenses", tags=["licenses"])
settings = get_settings()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.get("", response_model=list[LicenseOut])
def list_licenses(
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "licensing-officer", "auditor", "viewer")
    ),
):
    return license_service.list(db)


@router.get("/{license_id}", response_model=LicenseOut)
def get_license(
    license_id: str,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "licensing-officer", "auditor", "viewer")
    ),
):
    entity = license_service.get(db, license_id)
    if not entity:
        raise HTTPException(status_code=404, detail="License not found")
    return entity


@router.post("", response_model=LicenseOut, status_code=status.HTTP_201_CREATED)
def create_license(
    payload: LicenseCreate,
    request: Request,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "licensing-officer")),
):
    request_hash = payload_hash(payload.model_dump())
    if idempotency_key:
        cached = idempotency_service.check(db, key=idempotency_key, route="POST:/licenses", request_hash=request_hash)
        if cached:
            code, body = cached
            return JSONResponse(status_code=code, content=body)

    result = license_service.create(
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
            route="POST:/licenses",
            request_hash=request_hash,
            status_code=201,
            body=body,
        )
        db.commit()
    return result


@router.post("/{license_id}/submit", response_model=LicenseOut)
def submit_license(
    license_id: str,
    payload: LicenseAction,
    request: Request,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "licensing-officer")),
):
    entity = license_service.transition(
        db,
        license_id=license_id,
        transition="submit",
        action=payload,
        actor=subject.subject,
        ip_address=_client_ip(request),
    )
    if not entity:
        raise HTTPException(status_code=404, detail="License not found")
    db.commit()
    return entity


@router.post("/{license_id}/review", response_model=LicenseOut)
def review_license(
    license_id: str,
    payload: LicenseAction,
    request: Request,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "licensing-officer")),
):
    entity = license_service.transition(
        db,
        license_id=license_id,
        transition="review",
        action=payload,
        actor=subject.subject,
        ip_address=_client_ip(request),
    )
    if not entity:
        raise HTTPException(status_code=404, detail="License not found")
    db.commit()
    return entity


@router.post("/{license_id}/approve", response_model=LicenseOut)
def approve_license(
    license_id: str,
    payload: LicenseAction,
    request: Request,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "licensing-officer")),
):
    entity = license_service.transition(
        db,
        license_id=license_id,
        transition="approve",
        action=payload,
        actor=subject.subject,
        ip_address=_client_ip(request),
    )
    if not entity:
        raise HTTPException(status_code=404, detail="License not found")
    db.commit()
    return entity


@router.post("/{license_id}/reject", response_model=LicenseOut)
def reject_license(
    license_id: str,
    payload: LicenseAction,
    request: Request,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "licensing-officer")),
):
    entity = license_service.transition(
        db,
        license_id=license_id,
        transition="reject",
        action=payload,
        actor=subject.subject,
        ip_address=_client_ip(request),
    )
    if not entity:
        raise HTTPException(status_code=404, detail="License not found")
    db.commit()
    return entity


@router.post("/{license_id}/revoke", response_model=LicenseOut)
def revoke_license(
    license_id: str,
    payload: LicenseAction,
    request: Request,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "licensing-officer")),
):
    entity = license_service.transition(
        db,
        license_id=license_id,
        transition="revoke",
        action=payload,
        actor=subject.subject,
        ip_address=_client_ip(request),
    )
    if not entity:
        raise HTTPException(status_code=404, detail="License not found")
    db.commit()
    return entity


@router.get("/{license_id}/documents", response_model=list[DocumentOut])
def list_license_documents(
    license_id: str,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "licensing-officer", "auditor", "viewer")
    ),
):
    return document_service.list(db, aggregate_type="license", aggregate_id=license_id)


@router.post("/{license_id}/documents", response_model=DocumentOut, status_code=status.HTTP_201_CREATED)
async def upload_license_document(
    license_id: str,
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "licensing-officer")),
):
    payload = await file.read()
    if len(payload) > settings.max_upload_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    if file.content_type not in settings.allowed_file_types:
        raise HTTPException(status_code=415, detail="Unsupported media type")
    license_record = license_service.get(db, license_id)
    if not license_record:
        raise HTTPException(status_code=404, detail="License not found")
    result = document_service.upload(
        db,
        aggregate_type="license",
        aggregate_id=license_id,
        property_id=license_record.property_id,
        license_id=license_id,
        filename=file.filename or "upload.bin",
        media_type=file.content_type or "application/octet-stream",
        payload=payload,
        actor=subject.subject,
        ip_address=_client_ip(request),
    )
    db.commit()
    return result
