from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LicenseCreate(BaseModel):
    application_number: str = Field(min_length=3, max_length=64)
    property_id: str
    license_type: str
    applicant_name: str
    applicant_contact: str | None = None
    notes: str | None = None


class LicenseAction(BaseModel):
    comments: str | None = None
    assignee: str | None = None


class LicenseOut(BaseModel):
    id: str
    application_number: str
    property_id: str
    license_type: str
    status: str
    applicant_name: str
    applicant_contact: str | None
    current_assignee: str | None
    submitted_at: datetime | None
    decided_at: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
