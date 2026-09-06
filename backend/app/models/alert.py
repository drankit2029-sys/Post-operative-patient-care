from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AlertPriority

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(
        String(64), 
        ForeignKey("patients.patient_id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[AlertPriority] = mapped_column(
        SQLEnum(AlertPriority), 
        default=AlertPriority.MEDIUM, 
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="alerts")
