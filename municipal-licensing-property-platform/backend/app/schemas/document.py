from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    id: str
    aggregate_type: str
    aggregate_id: str
    storage_path: str
    original_filename: str
    media_type: str
    sha256: str
    size_bytes: int
    uploaded_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
