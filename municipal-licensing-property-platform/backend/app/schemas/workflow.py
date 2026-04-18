from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WorkflowEventOut(BaseModel):
    id: str
    aggregate_type: str
    aggregate_id: str
    action: str
    from_state: str | None
    to_state: str | None
    actor_subject: str
    comments: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
