from typing import List, Optional
from pydantic import BaseModel, Field

class ExtractedMedication(BaseModel):
    medication_name: Optional[str] = Field(default="",description="Name of the prescribed drug")
    dosage: Optional[str]= Field(default="",description="Dosage (e.g., 20 mg, 81 mg)")
    frequency: Optional[str] = Field(default="",description="Frequency (e.g., Once daily, Twice daily)")
    duration: Optional[str]= Field(default="Ongoing", description="Duration of therapy")

class ExtractedInstruction(BaseModel):
    instruction: Optional[str] = Field(description="Actionable discharge recovery instruction")

class ExtractedReminder(BaseModel):
    frequency: Optional[str] = Field(default="daily", description="'once' or 'daily'")
    time: Optional[str] = Field(default="",description="24-hour target time format 'HH:MM'")
    content: Optional[str] = Field(default="",description="Actionable reminder prompt text")

class ExtractedMonitor(BaseModel):
    frequency: Optional[str] = Field(default="daily", description="'once', 'daily', 'per_week', 'per_month'")
    input_type: Optional[str] = Field(default="image", description="'image' or 'video'")
    time: Optional[str] = Field(default="", description="24-hour target time format 'HH:MM'")
    instructions: Optional[str] = Field(default="",description="Clear patient instruction for photo or video capture")
    things_to_evaluate: Optional[str] = Field(default="",description="Clinical parameters or wound signs to examine")
    trigger_alert_if: Optional[str] = Field(default="",description="Explicit condition threshold that raises an alert")

class ParsedDischargeSummary(BaseModel):
    patient_id: Optional[str] = Field(default="PT-123",description="Standardized patient ID (e.g. PT-940)")
    name: Optional[str] = Field(default="Ankit",description="Patient full legal name")
    age: Optional[int] = Field(default=10, description="Patient age in years")
    gender: Optional[str] = Field(default="", description="'Male', 'Female', or 'Other'")
    admission_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    discharge_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    primary_diagnosis: Optional[str] = Field(default="", description="Primary discharge diagnosis")
    hospital_course_description: Optional[str] = Field(default="",description="Summary of admission course and interventions")
    physician_name: Optional[str] = Field(default="", description="Attending/responsible physician name")
    physician_contact: Optional[str] = Field(default="", description="Physician phone number or clinic desk")
    caretaker_name: Optional[str] = Field(default="", description="Designated family member or caretaker")
    caretaker_contact: Optional[str] = Field(default="", description="Caretaker telephone number")
    caretaker_relationship: Optional[str] = Field(default="", description="Relationship to patient")
    medications_at_discharge: List[ExtractedMedication] = Field(default_factory=list)
    discharge_instructions: List[ExtractedInstruction] = Field(default_factory=list)
    reminders: List[ExtractedReminder] = Field(default_factory=list)
    monitors: List[ExtractedMonitor] = Field(default_factory=list)
