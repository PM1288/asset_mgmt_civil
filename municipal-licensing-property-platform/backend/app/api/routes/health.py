from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.health import HealthEnvelope
from app.services.health_service import health_service

router = APIRouter(tags=["health"])


@router.get("/health/live", response_model=HealthEnvelope, include_in_schema=False)
def live() -> HealthEnvelope:
    return health_service.live()


@router.get("/health/ready", response_model=HealthEnvelope, include_in_schema=False)
def ready(db: Session = Depends(get_db)) -> HealthEnvelope:
    return health_service.readiness(db)


@router.get("/health/startup", response_model=HealthEnvelope, include_in_schema=False)
def startup() -> HealthEnvelope:
    return health_service.startup()
