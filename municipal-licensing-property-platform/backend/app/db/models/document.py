from __future__ import annotations

from sqlalchemy import BigInteger, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DocumentRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "documents"
    __table_args__ = (
        Index("ix_documents_aggregate", "aggregate_type", "aggregate_id"),
    )

    aggregate_type: Mapped[str] = mapped_column(String(32), nullable=False)
    aggregate_id: Mapped[str] = mapped_column(String(36), nullable=False)
    property_id: Mapped[str | None] = mapped_column(ForeignKey("properties.id", ondelete="SET NULL"), nullable=True)
    license_id: Mapped[str | None] = mapped_column(ForeignKey("license_applications.id", ondelete="SET NULL"), nullable=True)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False, unique=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    media_type: Mapped[str] = mapped_column(String(128), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    uploaded_by: Mapped[str] = mapped_column(String(128), nullable=False)

    property_ref = relationship("Property", back_populates="documents")
    license_ref = relationship("LicenseApplication", back_populates="documents")
