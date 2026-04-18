from __future__ import annotations

from app.db.session import SessionLocal
from app.services.maintenance_service import maintenance_service
from app.tasks.celery_app import celery_app
from app.telemetry.metrics import BACKGROUND_TASKS_TOTAL


@celery_app.task(name="maintenance.cleanup")
def cleanup():
    db = SessionLocal()
    try:
        result = maintenance_service.cleanup(db, actor="scheduler", ip_address=None)
        db.commit()
        BACKGROUND_TASKS_TOTAL.labels(task_name="cleanup", outcome="success").inc()
        return result
    except Exception:  # noqa: BLE001
        db.rollback()
        BACKGROUND_TASKS_TOTAL.labels(task_name="cleanup", outcome="failure").inc()
        raise
    finally:
        db.close()
