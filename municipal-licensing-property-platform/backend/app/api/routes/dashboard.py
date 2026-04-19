from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import SubjectContext, require_roles
from app.db.session import get_db
from app.schemas.dashboard import (
    DashboardComplianceOut,
    DashboardHealthSummaryOut,
    DashboardQueuesOut,
    DashboardRecentActivityOut,
    DashboardSummaryOut,
)
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryOut)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "licensing-officer", "auditor", "viewer", "operator")
    ),
):
    return dashboard_service.summary(db)


@router.get("/queues", response_model=DashboardQueuesOut)
def get_dashboard_queues(
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "licensing-officer", "auditor", "viewer", "operator")
    ),
):
    return dashboard_service.queues(db)


@router.get("/recent-activity", response_model=DashboardRecentActivityOut)
def get_dashboard_recent_activity(
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "licensing-officer", "auditor", "viewer", "operator")
    ),
):
    return dashboard_service.recent_activity(db)


@router.get("/upcoming-renewals", response_model=DashboardComplianceOut)
def get_dashboard_compliance(
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "licensing-officer", "auditor", "viewer", "operator")
    ),
):
    return dashboard_service.compliance(db)


@router.get("/health-summary", response_model=DashboardHealthSummaryOut)
def get_dashboard_health_summary(
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "licensing-officer", "auditor", "viewer", "operator")
    ),
):
    return dashboard_service.health_summary(db)
