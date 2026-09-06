from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class PastReminderEvent(Base):
    __tablename__ = "past_reminder_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(
        String(64), 
        ForeignKey("patients.patient_id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_or_not: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="past_reminder_events")


class PastMonitorEvent(Base):
    __tablename__ = "past_monitor_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(
        String(64), 
        ForeignKey("patients.patient_id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    input_given: Mapped[str] = mapped_column(Text, nullable=False)
    remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    alert_triggered_or_not: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="past_monitor_events")
