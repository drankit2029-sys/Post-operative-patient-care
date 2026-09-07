from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class PastReminderEventBase(BaseModel):
    patient_id: str
    reminder_id: Optional[int] = None
    content: str
    resolved_or_not: bool = False

class PastReminderEventCreate(PastReminderEventBase):
    pass

class PastReminderEventResponse(PastReminderEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PastMonitorEventBase(BaseModel):
    patient_id: str
    monitor_id: Optional[int] = None
    input_given: str
    remark: Optional[str] = None
    alert_triggered_or_not: bool = False

class PastMonitorEventCreate(PastMonitorEventBase):
    pass

class PastMonitorEventResponse(PastMonitorEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
