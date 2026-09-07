from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AlertPriority

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.reminder import Reminder
    from app.models.monitor import Monitor

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(
        String(64), 
        ForeignKey("patients.patient_id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    reminder_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("reminders.id", ondelete="CASCADE"), 
        index=True, 
        nullable=True
    )
    monitor_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("monitors.id", ondelete="CASCADE"), 
        index=True, 
        nullable=True
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
    reminder: Mapped[Optional["Reminder"]] = relationship("Reminder", back_populates="alerts")
    monitor: Mapped[Optional["Monitor"]] = relationship("Monitor", back_populates="alerts")
