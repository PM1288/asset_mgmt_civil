from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class LicenseApplication(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "license_applications"
    __table_args__ = (
        Index("ix_license_applications_application_number_status", "application_number", "status"),
    )

    application_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    property_id: Mapped[str] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)
    license_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    applicant_name_enc: Mapped[str] = mapped_column(Text, nullable=False)
    applicant_contact_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    current_assignee: Mapped[str | None] = mapped_column(String(128), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes_enc: Mapped[str | None] = mapped_column(Text, nullable=True)

    property_ref = relationship("Property", back_populates="licenses")
    workflow_events = relationship("WorkflowEvent", back_populates="license_ref", cascade="all, delete-orphan")
    documents = relationship("DocumentRecord", back_populates="license_ref")
