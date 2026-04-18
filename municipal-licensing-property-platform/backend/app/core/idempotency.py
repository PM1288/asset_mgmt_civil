from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import Conflict
from app.db.models import IdempotencyRecord


def payload_hash(payload: dict) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class IdempotencyService:
    def check(self, db: Session, *, key: str, route: str, request_hash: str) -> tuple[int, dict] | None:
        record = db.scalar(select(IdempotencyRecord).where(IdempotencyRecord.key == key))
        if not record:
            return None
        if record.route != route or record.request_hash != request_hash:
            raise Conflict("Idempotency key re-used with a different request")
        try:
            expiry = datetime.fromisoformat(record.expires_at)
        except ValueError:
            expiry = datetime.now(timezone.utc)
        if expiry < datetime.now(timezone.utc):
            return None
        return record.status_code, json.loads(record.response_body)

    def store(self, db: Session, *, key: str, route: str, request_hash: str, status_code: int, body: dict) -> None:
        settings = get_settings()
        expiry = datetime.now(timezone.utc) + timedelta(hours=settings.idempotency_ttl_hours)
        record = IdempotencyRecord(
            key=key,
            route=route,
            request_hash=request_hash,
            status_code=status_code,
            response_body=json.dumps(body, ensure_ascii=False),
            expires_at=expiry.isoformat(),
        )
        db.add(record)
        db.flush()


idempotency_service = IdempotencyService()
