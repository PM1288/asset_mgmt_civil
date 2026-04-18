from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PropertyBase(BaseModel):
    property_number: str = Field(min_length=3, max_length=64)
    ward_code: str
    address_line_1: str
    address_line_2: str | None = None
    city: str = "Pune"
    district: str = "Pune"
    state: str = "Maharashtra"
    postal_code: str | None = None
    geo_lat: float | None = None
    geo_lng: float | None = None
    status: str = "active"
    use_type: str = "mixed_use"
    owner_name: str
    owner_contact: str | None = None
    assessment_zone: str | None = None
    remarks: str | None = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    ward_code: str | None = None
    address_line_1: str | None = None
    address_line_2: str | None = None
    city: str | None = None
    district: str | None = None
    state: str | None = None
    postal_code: str | None = None
    geo_lat: float | None = None
    geo_lng: float | None = None
    status: str | None = None
    use_type: str | None = None
    owner_name: str | None = None
    owner_contact: str | None = None
    assessment_zone: str | None = None
    remarks: str | None = None


class PropertyOut(PropertyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
