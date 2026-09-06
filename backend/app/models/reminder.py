from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ReminderFrequency

class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    patient_id: Mapped[str] = mapped_column(
        String(64), 
        ForeignKey("patients.patient_id", ondelete="CASCADE"), 
        index=True, 
        nullable=False
    )
    frequency: Mapped[ReminderFrequency] = mapped_column(
        SQLEnum(ReminderFrequency), 
        default=ReminderFrequency.DAILY, 
        nullable=False
    )
    time: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    patient: Mapped["Patient"] = relationship("Patient", back_populates="reminders")
