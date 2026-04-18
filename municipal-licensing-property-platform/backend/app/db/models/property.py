from __future__ import annotations

from sqlalchemy import Float, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Property(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "properties"
    __table_args__ = (
        Index("ix_properties_property_number_status", "property_number", "status"),
    )

    property_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    ward_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    address_line_1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(128), nullable=False, default="Pune")
    district: Mapped[str] = mapped_column(String(128), nullable=False, default="Pune")
    state: Mapped[str] = mapped_column(String(128), nullable=False, default="Maharashtra")
    postal_code: Mapped[str | None] = mapped_column(String(16), nullable=True)
    geo_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    geo_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    use_type: Mapped[str] = mapped_column(String(64), nullable=False, default="mixed_use")
    owner_name_enc: Mapped[str] = mapped_column(Text, nullable=False)
    owner_contact_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessment_zone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    remarks_enc: Mapped[str | None] = mapped_column(Text, nullable=True)

    licenses = relationship("LicenseApplication", back_populates="property_ref", cascade="all, delete-orphan")
    documents = relationship("DocumentRecord", back_populates="property_ref")
