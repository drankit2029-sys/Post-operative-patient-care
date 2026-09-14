from datetime import date, datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, Date, DateTime, ForeignKey,Text, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import TaskStatus

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.reminder import Reminder
    from app.models.monitor import Monitor

class ReminderTaskInstance(Base):
    __tablename__ = "reminder_task_instances"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    reminder_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("reminders.id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    patient_id: Mapped[str] = mapped_column(
        String(64), 
        ForeignKey("patients.patient_id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    scheduled_time: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), 
        default=TaskStatus.PENDING, 
        nullable=False, 
        index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="reminder_task_instances")
    reminder: Mapped["Reminder"] = relationship("Reminder", back_populates="task_instances")

class MonitorTaskInstance(Base):
    __tablename__ = "monitor_task_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    monitor_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("monitors.id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    patient_id: Mapped[str] = mapped_column(
        String(64), 
        ForeignKey("patients.patient_id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )

    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    scheduled_time: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.PENDING, nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    input_given: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
  
    # Relationships
    patient: Mapped["Patient"] = relationship("Patient", back_populates="monitor_task_instances")
    monitor: Mapped["Monitor"] = relationship("Monitor", back_populates="task_instances")