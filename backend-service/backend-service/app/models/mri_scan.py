import uuid

from sqlalchemy import String, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class MRIScan(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "mri_scans"

    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    left_scan_path: Mapped[str] = mapped_column(String(500), nullable=False)
    right_scan_path: Mapped[str] = mapped_column(String(500), nullable=False)
    scanned_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    patient = relationship("Patient", back_populates="mri_scans")