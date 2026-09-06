from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import ReminderFrequency

class ReminderBase(BaseModel):
    patient_id: str
    frequency: ReminderFrequency = ReminderFrequency.DAILY
    time: str = Field(..., description="Time formatted as HH:MM", examples=["08:30"])
    content: str

class ReminderCreate(ReminderBase):
    pass

class ReminderResponse(ReminderBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
