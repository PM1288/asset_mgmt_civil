from __future__ import annotations

import logging
import shutil

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


def run_preflight() -> None:
    settings = get_settings()

    for path in [settings.logs_root, settings.docs_root, settings.backups_root, settings.runtime_root]:
        path.mkdir(parents=True, exist_ok=True)

    usage = shutil.disk_usage(settings.docs_root)
    free_mb = usage.free // (1024 * 1024)
    if free_mb < settings.minimum_free_disk_mb:
        raise RuntimeError(
            f"Not enough free disk for safe startup. Required={settings.minimum_free_disk_mb}MB available={free_mb}MB"
        )

    db: Session = SessionLocal()
    try:
        db.execute(text("select 1"))
    finally:
        db.close()

    logger.info("startup preflight complete")
