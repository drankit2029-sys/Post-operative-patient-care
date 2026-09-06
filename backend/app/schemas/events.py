from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Past Reminder Event Schemas
class PastReminderEventBase(BaseModel):
    patient_id: str
    content: str
    resolved_or_not: bool = False

class PastReminderEventCreate(PastReminderEventBase):
    pass

class PastReminderEventResponse(PastReminderEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Past Monitor Event Schemas
class PastMonitorEventBase(BaseModel):
    patient_id: str
    input_given: str
    remark: Optional[str] = None
    alert_triggered_or_not: bool = False

class PastMonitorEventCreate(PastMonitorEventBase):
    pass

class PastMonitorEventResponse(PastMonitorEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
