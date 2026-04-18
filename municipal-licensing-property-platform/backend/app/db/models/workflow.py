from __future__ import annotations

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class WorkflowEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workflow_events"
    __table_args__ = (
        Index("ix_workflow_events_aggregate", "aggregate_type", "aggregate_id"),
    )

    aggregate_type: Mapped[str] = mapped_column(String(32), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    from_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
    actor_subject: Mapped[str] = mapped_column(String(128), nullable=False)
    comments_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    license_id: Mapped[str | None] = mapped_column(ForeignKey("license_applications.id", ondelete="CASCADE"), nullable=True)

    license_ref = relationship("LicenseApplication", back_populates="workflow_events")
