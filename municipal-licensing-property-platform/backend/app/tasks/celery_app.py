from __future__ import annotations

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "municipal_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.maintenance", "app.tasks.backups"],
)

celery_app.conf.update(
    task_default_queue="municipal-default",
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    task_track_started=True,
    timezone=settings.timezone,
    enable_utc=False,
    task_soft_time_limit=settings.celery_task_soft_time_limit_seconds,
    task_time_limit=settings.celery_task_hard_time_limit_seconds,
    beat_schedule={
        "daily-cleanup": {
            "task": "maintenance.cleanup",
            "schedule": 60 * 60 * 6,
        },
        "nightly-backup": {
            "task": "backups.run",
            "schedule": 60 * 60 * 24,
        },
        "weekly-backup-validation": {
            "task": "backups.validate_latest",
            "schedule": 60 * 60 * 24 * 7,
        },
    },
)
