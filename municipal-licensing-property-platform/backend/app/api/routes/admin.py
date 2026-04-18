from __future__ import annotations

import shutil

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import SubjectContext, require_roles
from app.db.repositories.audits import AuditRepository
from app.db.session import get_db
from app.schemas.common import AuditLogOut, Message
from app.services.backup_service import backup_service
from app.services.health_service import health_service
from app.services.maintenance_service import maintenance_service

router = APIRouter(prefix="/admin", tags=["admin"])
settings = get_settings()


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


@router.get("/audit", response_model=list[AuditLogOut])
def list_audit(
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "auditor", "operator")),
):
    repo = AuditRepository()
    return repo.list_recent(db, limit=200)


@router.post("/maintenance/cleanup")
def trigger_cleanup(
    request: Request,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "operator")),
):
    result = maintenance_service.cleanup(db, actor=subject.subject, ip_address=_client_ip(request))
    db.commit()
    return result


@router.get("/diagnostics/dependencies")
def diagnostics(
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(require_roles("municipal-admin", "operator", "auditor")),
):
    readiness = health_service.readiness(db).model_dump()
    usage = shutil.disk_usage(settings.docs_root)
    return {
        "readiness": readiness,
        "disk": {
            "total_mb": usage.total // (1024 * 1024),
            "used_mb": usage.used // (1024 * 1024),
            "free_mb": usage.free // (1024 * 1024),
        },
        "limits": {
            "disk_pressure_threshold_percent": settings.disk_pressure_threshold_percent,
            "minimum_free_disk_mb": settings.minimum_free_disk_mb,
        },
    }


@router.post("/backups/run")
def run_backup(
    subject: SubjectContext = Depends(require_roles("municipal-admin", "operator")),
):
    return backup_service.create_backup_bundle()


@router.post("/backups/validate-latest")
def validate_latest_backup(
    subject: SubjectContext = Depends(require_roles("municipal-admin", "operator")),
):
    backups = sorted(
        [item for item in settings.backups_root.iterdir() if item.is_dir()],
        key=lambda item: item.name,
        reverse=True,
    )
    if not backups:
        return {"ok": False, "detail": "No backups present"}
    return backup_service.validate_backup_bundle(backups[0])
