from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import (
    TreatmentSummaryItem,
    MedicationItem,
    DischargeInstructionItem,
    FollowUpAppointmentItem,
    PhysicianInfo,
    NoteItem,
    CaretakerInfo
)
from app.schemas.alert import AlertResponse
from app.schemas.reminder import ReminderResponse
from app.schemas.monitor import MonitorResponse
from app.schemas.events import PastReminderEventResponse, PastMonitorEventResponse

class PatientBase(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None
    primary_diagnosis: Optional[str] = None
    hospital_course_description: Optional[str] = None
    treatment_summary: List[TreatmentSummaryItem] = Field(default_factory=list)
    medications_at_discharge: List[MedicationItem] = Field(default_factory=list)
    discharge_instructions: List[DischargeInstructionItem] = Field(default_factory=list)
    follow_up_appointments: List[FollowUpAppointmentItem] = Field(default_factory=list)
    responsible_physician: Optional[PhysicianInfo] = None
    additional_notes: List[NoteItem] = Field(default_factory=list)
    caretaker: Optional[CaretakerInfo] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    admission_date: Optional[date] = None
    discharge_date: Optional[date] = None
    primary_diagnosis: Optional[str] = None
    hospital_course_description: Optional[str] = None
    treatment_summary: Optional[List[TreatmentSummaryItem]] = None
    medications_at_discharge: Optional[List[MedicationItem]] = None
    discharge_instructions: Optional[List[DischargeInstructionItem]] = None
    follow_up_appointments: Optional[List[FollowUpAppointmentItem]] = None
    responsible_physician: Optional[PhysicianInfo] = None
    additional_notes: Optional[List[NoteItem]] = None
    caretaker: Optional[CaretakerInfo] = None

class PatientResponse(PatientBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PatientDetailResponse(PatientResponse):
    alerts: List[AlertResponse] = Field(default_factory=list)
    reminders: List[ReminderResponse] = Field(default_factory=list)
    monitors: List[MonitorResponse] = Field(default_factory=list)
    past_reminder_events: List[PastReminderEventResponse] = Field(default_factory=list)
    past_monitor_events: List[PastMonitorEventResponse] = Field(default_factory=list)
