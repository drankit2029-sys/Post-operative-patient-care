from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.enums import MonitorFrequency, InputType

class MonitorBase(BaseModel):
    patient_id: str
    frequency: MonitorFrequency = MonitorFrequency.DAILY
    input_type: InputType
    time: str = Field(..., description="Time formatted as HH:MM", examples=["14:00"])
    instructions: str
    things_to_evaluate: str
    trigger_alert_if: str

class MonitorCreate(MonitorBase):
    pass

class MonitorResponse(MonitorBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
