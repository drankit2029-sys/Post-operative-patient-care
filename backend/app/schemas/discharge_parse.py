from typing import List, Optional
from pydantic import BaseModel, Field

class ExtractedMedication(BaseModel):
    medication_name: str = Field(description="Name of the prescribed drug")
    dosage: str = Field(description="Dosage (e.g., 20 mg, 81 mg)")
    frequency: str = Field(description="Frequency (e.g., Once daily, Twice daily)")
    duration: str = Field(default="Ongoing", description="Duration of therapy")

class ExtractedInstruction(BaseModel):
    instruction: str = Field(description="Actionable discharge recovery instruction")

class ExtractedReminder(BaseModel):
    frequency: str = Field(default="daily", description="'once' or 'daily'")
    time: str = Field(description="24-hour target time format 'HH:MM'")
    content: str = Field(description="Actionable reminder prompt text")

class ExtractedMonitor(BaseModel):
    frequency: str = Field(default="daily", description="'once', 'daily', 'per_week', 'per_month'")
    input_type: str = Field(default="image", description="'image' or 'video'")
    time: str = Field(description="24-hour target time format 'HH:MM'")
    instructions: str = Field(description="Clear patient instruction for photo or video capture")
    things_to_evaluate: str = Field(description="Clinical parameters or wound signs to examine")
    trigger_alert_if: str = Field(description="Explicit condition threshold that raises an alert")

class ParsedDischargeSummary(BaseModel):
    patient_id: str = Field(description="Standardized patient ID (e.g. PT-940)")
    name: str = Field(description="Patient full legal name")
    age: int = Field(description="Patient age in years")
    gender: str = Field(description="'Male', 'Female', or 'Other'")
    admission_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    discharge_date: Optional[str] = Field(default=None, description="YYYY-MM-DD")
    primary_diagnosis: str = Field(description="Primary discharge diagnosis")
    hospital_course_description: str = Field(description="Summary of admission course and interventions")
    physician_name: Optional[str] = Field(default="", description="Attending/responsible physician name")
    physician_contact: Optional[str] = Field(default="", description="Physician phone number or clinic desk")
    caretaker_name: Optional[str] = Field(default="", description="Designated family member or caretaker")
    caretaker_contact: Optional[str] = Field(default="", description="Caretaker telephone number")
    caretaker_relationship: Optional[str] = Field(default="", description="Relationship to patient")
    medications_at_discharge: List[ExtractedMedication] = Field(default_factory=list)
    discharge_instructions: List[ExtractedInstruction] = Field(default_factory=list)
    reminders: List[ExtractedReminder] = Field(default_factory=list)
    monitors: List[ExtractedMonitor] = Field(default_factory=list)
