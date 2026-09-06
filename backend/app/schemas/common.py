from pydantic import BaseModel, Field
from typing import Optional

class TreatmentSummaryItem(BaseModel):
    treatment_name: str
    duration: str
    treatment_notes: str

class MedicationItem(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    duration: str

class DischargeInstructionItem(BaseModel):
    instruction: str

class FollowUpAppointmentItem(BaseModel):
    date: str
    department: str
    provider: str

class PhysicianInfo(BaseModel):
    name: str
    contact: str

class NoteItem(BaseModel):
    note: str

class CaretakerInfo(BaseModel):
    name: str
    contact: str
    relationship: str
