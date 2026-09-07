from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import AlertPriority

class AlertBase(BaseModel):
    patient_id: str
    reminder_id: Optional[int] = None
    monitor_id: Optional[int] = None
    content: str
    priority: AlertPriority = AlertPriority.MEDIUM

class AlertCreate(AlertBase):
    pass

class AlertResponse(AlertBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
