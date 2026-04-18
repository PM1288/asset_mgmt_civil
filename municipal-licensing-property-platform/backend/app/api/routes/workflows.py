from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import SubjectContext, require_roles
from app.db.session import get_db
from app.schemas.workflow import WorkflowEventOut
from app.services.workflow_service import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/{aggregate_type}/{aggregate_id}", response_model=list[WorkflowEventOut])
def get_workflow_history(
    aggregate_type: str,
    aggregate_id: str,
    db: Session = Depends(get_db),
    subject: SubjectContext = Depends(
        require_roles("municipal-admin", "property-officer", "licensing-officer", "auditor", "viewer")
    ),
):
    return workflow_service.list(db, aggregate_type, aggregate_id)
