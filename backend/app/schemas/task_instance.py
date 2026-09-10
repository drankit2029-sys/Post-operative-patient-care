from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import TaskStatus

class ReminderTaskInstanceBase(BaseModel):
    reminder_id: int
    patient_id: str
    scheduled_date: date
    scheduled_time: str
    status: TaskStatus = TaskStatus.PENDING
    completed_at: Optional[datetime] = None

class ReminderTaskInstanceCreate(ReminderTaskInstanceBase):
    pass

class ReminderTaskInstanceUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    completed_at: Optional[datetime] = None

class ReminderTaskInstanceResponse(ReminderTaskInstanceBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
