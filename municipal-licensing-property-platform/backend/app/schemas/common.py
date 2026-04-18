from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    detail: str


class AuditLogOut(BaseModel):
    id: str
    event_type: str
    subject: str | None
    actor: str | None
    outcome: str
    ip_address: str | None
    detail_message: str | None
    details_json: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
