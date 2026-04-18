from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from app.core.config import get_settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        request_id = getattr(record, "request_id", None)
        subject = getattr(record, "subject", None)
        if request_id:
            payload["request_id"] = request_id
        if subject:
            payload["subject"] = subject
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _build_handler(file_path: Path, max_bytes: int, backup_count: int) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(JsonFormatter())
    return handler


def configure_logging() -> None:
    settings = get_settings()

    root = logging.getLogger()
    root.setLevel(getattr(logging, settings.log_level))
    root.handlers.clear()

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(JsonFormatter())
    root.addHandler(console)

    app_file = settings.logs_root / settings.app_log_name
    audit_file = settings.logs_root / settings.audit_log_name

    root.addHandler(_build_handler(app_file, settings.log_max_bytes, settings.log_backup_count))

    audit_logger = logging.getLogger("audit")
    audit_logger.handlers.clear()
    audit_logger.setLevel(logging.INFO)
    audit_logger.propagate = False
    audit_logger.addHandler(console)
    audit_logger.addHandler(
        _build_handler(audit_file, settings.log_max_bytes, settings.log_backup_count)
    )

    logging.getLogger("uvicorn").handlers = root.handlers.copy()
    logging.getLogger("uvicorn.access").handlers = root.handlers.copy()
    logging.getLogger("uvicorn.error").handlers = root.handlers.copy()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
