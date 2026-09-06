from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import MonitorFrequency, InputType

class Monitor(Base):
    __tablename__ = "monitors"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(
        String(64), 
        ForeignKey("patients.patient_id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    frequency: Mapped[MonitorFrequency] = mapped_column(
        SQLEnum(MonitorFrequency), 
        default=MonitorFrequency.DAILY, 
        nullable=False
    )
    input_type: Mapped[InputType] = mapped_column(
        SQLEnum(InputType), 
        nullable=False
    )
    time: Mapped[str] = mapped_column(String(32), nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    things_to_evaluate: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_alert_if: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="monitors")
