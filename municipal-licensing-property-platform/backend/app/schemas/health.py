from __future__ import annotations

from pydantic import BaseModel


class ComponentHealth(BaseModel):
    name: str
    ok: bool
    detail: str


class HealthEnvelope(BaseModel):
    status: str
    components: list[ComponentHealth]
