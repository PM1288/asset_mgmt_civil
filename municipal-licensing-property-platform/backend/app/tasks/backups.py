from __future__ import annotations

from app.services.backup_service import backup_service
from app.tasks.celery_app import celery_app
from app.telemetry.metrics import BACKGROUND_TASKS_TOTAL


@celery_app.task(name="backups.run")
def run_backup():
    try:
        result = backup_service.create_backup_bundle()
        BACKGROUND_TASKS_TOTAL.labels(task_name="backup", outcome="success").inc()
        return result
    except Exception:  # noqa: BLE001
        BACKGROUND_TASKS_TOTAL.labels(task_name="backup", outcome="failure").inc()
        raise


@celery_app.task(name="backups.validate_latest")
def validate_latest():
    try:
        backups = sorted(
            [item for item in backup_service.settings.backups_root.iterdir() if item.is_dir()],
            key=lambda item: item.name,
            reverse=True,
        )
        if not backups:
            return {"ok": False, "detail": "No backups present"}
        result = backup_service.validate_backup_bundle(backups[0])
        BACKGROUND_TASKS_TOTAL.labels(task_name="backup_validate", outcome="success").inc()
        return result
    except Exception:  # noqa: BLE001
        BACKGROUND_TASKS_TOTAL.labels(task_name="backup_validate", outcome="failure").inc()
        raise
