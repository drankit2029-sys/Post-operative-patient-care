from datetime import date, datetime
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from sqlalchemy import String, Integer, Text, Date, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.alert import Alert
    from app.models.reminder import Reminder
    from app.models.monitor import Monitor
    from app.models.events import PastReminderEvent, PastMonitorEvent
    from app.models.task_instance import ReminderTaskInstance

class Patient(Base):
    __tablename__ = "patients"

    patient_id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(32), nullable=False)

    admission_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    discharge_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    primary_diagnosis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hospital_course_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    treatment_summary: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    medications_at_discharge: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    discharge_instructions: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    follow_up_appointments: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    responsible_physician: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    additional_notes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list)
    caretaker: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    alerts: Mapped[List["Alert"]] = relationship(
        "Alert", 
        back_populates="patient", 
        cascade="all, delete-orphan"
    )
    reminders: Mapped[List["Reminder"]] = relationship(
        "Reminder", 
        back_populates="patient", 
        cascade="all, delete-orphan"
    )
    monitors: Mapped[List["Monitor"]] = relationship(
        "Monitor", 
        back_populates="patient", 
        cascade="all, delete-orphan"
    )
    past_reminder_events: Mapped[List["PastReminderEvent"]] = relationship(
        "PastReminderEvent", 
        back_populates="patient", 
        cascade="all, delete-orphan"
    )
    past_monitor_events: Mapped[List["PastMonitorEvent"]] = relationship(
        "PastMonitorEvent", 
        back_populates="patient", 
        cascade="all, delete-orphan"
    )
    reminder_task_instances: Mapped[List["ReminderTaskInstance"]] = relationship(
        "ReminderTaskInstance", 
        back_populates="patient", 
        cascade="all, delete-orphan"
    )
