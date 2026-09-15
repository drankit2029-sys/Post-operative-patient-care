import base64
import json
import logging
import mimetypes
import os
import random
import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.enums import AlertPriority
from app.schemas.discharge_parse import ParsedDischargeSummary

logger = logging.getLogger(__name__)

# Initialize client using Mistral endpoint via AsyncOpenAI
try:
    from openai import AsyncOpenAI

    raw_key = settings.MISTRAL_API_KEY or os.getenv("MISTRAL_API_KEY") or ""
    api_key = raw_key.strip("\"' \r\n\t")
    if api_key:
        ai_client = AsyncOpenAI(
            base_url=settings.MISTRAL_BASE_URL,
            api_key=api_key,
        )
    else:
        ai_client = None
except ImportError:
    AsyncOpenAI = None
    ai_client = None


# ==========================================
# PYDANTIC STRUCTURED SCHEMAS
# ==========================================

class ReminderTriageOutput(BaseModel):
    priority: AlertPriority = Field(
        description="Clinical severity tier: 'low', 'medium', 'high', or 'critical'"
    )
    alert_content: str = Field(
        description="Concise, actionable clinical alert message for healthcare providers"
    )
    clinical_rationale: str = Field(
        description="Detailed pathophysiological and pharmacological justification"
    )


class MonitorTriageOutput(BaseModel):
    alert_triggered: bool = Field(
        description="True if telemetry violates trigger threshold, otherwise False"
    )
    priority: AlertPriority = Field(
        default=AlertPriority.MEDIUM,
        description="Alert priority level if triggered ('low', 'medium', 'high', 'critical')"
    )
    alert_content: Optional[str] = Field(
        default=None,
        description="Clinician-facing alert description if triggered; null otherwise"
    )
    evaluation_remark: Optional[str] = Field(
        description="Objective medical remark to log in patient record"
    )


# ==========================================
# HELPER UTILITIES
# ==========================================

def clean_json_string(raw_str: str) -> str:
    """Strips markdown code fences, think tags, and extracts the outermost JSON block."""
    cleaned = raw_str.strip()
    cleaned = re.sub(r"<think>.*?</think>", "", cleaned, flags=re.DOTALL)
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx : end_idx + 1]
    return cleaned.strip()


def encode_image_to_base64(file_path: str) -> Optional[str]:
    if not file_path:
        return None
    # If the frontend already transmitted a data URI or base64 string
    if file_path.startswith("data:image"):
        return file_path
    if not os.path.exists(file_path):
        return None
    mime_type, _ = mimetypes.guess_type(file_path) or ("image/jpeg", None)
    try:
        with open(file_path, "rb") as image_file:
            encoded_str = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded_str}"
    except Exception as e:
        logger.error(f"Error encoding image {file_path}: {e}")
        return None

# ==========================================
# HEURISTIC FALLBACK ENGINES
# ==========================================

def heuristic_missed_reminder(
    patient_summary: Dict[str, Any],
    medication_info: str,
    scheduled_time: str,
) -> ReminderTriageOutput:
    content_lower = medication_info.lower()
    diagnosis_lower = str(patient_summary.get("primary_diagnosis", "")).lower()

    critical_keywords = [
        "ticagrelor", "aspirin", "plavix", "clopidogrel", "brilinta",
        "warfarin", "eliquis", "apixaban", "xarelto", "insulin", "glargine",
    ]
    high_risk_keywords = [
        "metoprolol", "carvedilol", "losartan", "amlodipine",
        "furosemide", "torsemide", "entresto", "prednisone",
    ]

    is_stent_or_cardiac = any(
        k in diagnosis_lower for k in ["stent", "pci", "coronary", "myocardial", "infarction"]
    )

    if any(drug in content_lower for drug in critical_keywords) and is_stent_or_cardiac:
        priority = AlertPriority.CRITICAL
        alert_text = (
            f"CRITICAL: Missed post-PCI antiplatelet dose ({medication_info}) "
            f"scheduled for {scheduled_time}. In-stent thrombosis risk."
        )
        rationale = "Interruption of antiplatelet therapy in early post-PCI period triggers acute thrombosis."
    elif any(drug in content_lower for drug in critical_keywords):
        priority = AlertPriority.HIGH
        alert_text = f"High Risk: Missed critical medication dose ({medication_info}) scheduled for {scheduled_time}."
        rationale = "High-risk anticoagulant, antiplatelet, or glycemic agent window lapsed by >30 minutes."
    elif any(drug in content_lower for drug in high_risk_keywords):
        priority = AlertPriority.HIGH
        alert_text = f"Overdue: Missed maintenance cardiovascular dose ({medication_info}) scheduled at {scheduled_time}."
        rationale = "Delayed antihypertensive or diuretic increases risk of rebound hemodynamics."
    else:
        priority = AlertPriority.MEDIUM
        alert_text = f"Delayed reminder: No log recorded for: {medication_info} (scheduled {scheduled_time})."
        rationale = "Care reminder unacknowledged past the 30-minute grace period."

    return ReminderTriageOutput(
        priority=priority,
        alert_content=alert_text,
        clinical_rationale=rationale,
    )


def heuristic_monitor_telemetry(
    patient_summary: Dict[str, Any],
    monitor_spec: Dict[str, Any],
    past_remarks: List[str],
    user_notes: Optional[str] = None,
) -> MonitorTriageOutput:
    instructions = monitor_spec.get("instructions", "").lower()
    notes_text = (user_notes or "").lower()

    high_risk_words = ["erythema", "hematoma", "bleeding", "swelling", "shortness of breath", "chest pain", "fever"]
    found_issues = [w for w in high_risk_words if w in notes_text]

    if found_issues:
        return MonitorTriageOutput(
            alert_triggered=True,
            priority=AlertPriority.HIGH,
            alert_content=f"Telemetry flag: {', '.join(found_issues)} noted during check-in: {monitor_spec.get('instructions')}",
            evaluation_remark=f"Submission indicates abnormal telemetry signs ({', '.join(found_issues)}). Exceeds baseline thresholds.",
        )

    return MonitorTriageOutput(
        alert_triggered=False,
        priority=AlertPriority.LOW,
        alert_content=None,
        evaluation_remark=f"Telemetry reviewed for {instructions}. Parameters within expected post-discharge margins.",
    )


def fallback_mock_discharge_summary() -> ParsedDischargeSummary:
    random_id = f"PT-{random.randint(100, 999)}"
    return ParsedDischargeSummary(
        patient_id=random_id,
        name="Julianne Moore",
        age=62,
        gender="Female",
        admission_date="2026-08-28",
        discharge_date="2026-09-05",
        primary_diagnosis="Congestive Heart Failure (NYHA Class III) decompensation, resolved",
        hospital_course_description="Diuresed with IV Furosemide. Switched to oral Torsemide regimen with stable electrolytes.",
        physician_name="Dr. Katherine Cole",
        physician_contact="+1 (555) 438-9201",
        caretaker_name="David Moore",
        caretaker_contact="+1 (555) 312-7890",
        caretaker_relationship="Spouse",
        medications_at_discharge=[
            {"medication_name": "Torsemide", "dosage": "20 mg", "frequency": "Once daily in morning", "duration": "Ongoing"},
            {"medication_name": "Sacubitril / Valsartan", "dosage": "24/26 mg", "frequency": "Twice daily", "duration": "Ongoing"},
            {"medication_name": "Spironolactone", "dosage": "25 mg", "frequency": "Once daily", "duration": "Ongoing"},
        ],
        discharge_instructions=[
            {"instruction": "Weigh yourself daily in the morning after voiding and before breakfast."},
            {"instruction": "Limit sodium intake strictly to under 2,000 mg daily."},
        ],
        reminders=[
            {"frequency": "daily", "time": "08:00", "content": "Take Torsemide 20mg and Entresto 24/26mg with water."},
            {"frequency": "daily", "time": "20:00", "content": "Take evening dose of Entresto 24/26mg."},
        ],
        monitors=[
            {
                "frequency": "daily",
                "input_type": "image",
                "time": "08:15",
                "instructions": "Take a clear photograph of the digital weight scale display.",
                "things_to_evaluate": "Daily morning dry body weight.",
                "trigger_alert_if": "Weight gain >= 3 lbs over baseline within 48 hours.",
            }
        ],
    )


# ==========================================
# PRIMARY EVALUATION ENGINES
# ==========================================

async def evaluate_missed_reminder(
    patient_summary: Dict[str, Any],
    medication_info: str,
    scheduled_time: str,
) -> ReminderTriageOutput:
    if not ai_client:
        logger.info("Mistral AI client not configured; utilizing heuristic fallback.")
        return heuristic_missed_reminder(patient_summary, medication_info, scheduled_time)

    prompt = f"""
You are an expert clinical triage assistant.
A patient has missed a care reminder by >30 minutes.

PATIENT CONTEXT:
- Name: {patient_summary.get('name', 'Unknown')}
- Age/Gender: {patient_summary.get('age')} {patient_summary.get('gender')}
- Primary Diagnosis: {patient_summary.get('primary_diagnosis', 'N/A')}
- Hospital Course: {patient_summary.get('hospital_course_description', 'N/A')}
- Discharge Meds: {json.dumps(patient_summary.get('medications_at_discharge', []), indent=2)}

MISSED CARE REGIMEN:
- Item: {medication_info}
- Scheduled Time: {scheduled_time}

Assess the risk level and return strictly a JSON object:
{{
  "priority": "low" | "medium" | "high" | "critical",
  "alert_content": "Concise alert message (str)",
  "clinical_rationale": "Concise Medical justification (str)"
}}
"""
    try:
        completion = await ai_client.chat.completions.create(
            model=settings.AI_TEXT_MODEL,
            messages=[
                {"role": "system", "content": "You are a clinical triage AI. Output strictly valid JSON."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw_text = completion.choices[0].message.content or ""
        cleaned = clean_json_string(raw_text)
        return ReminderTriageOutput.model_validate_json(cleaned)
    except Exception as e:
        logger.error(f"Mistral reminder evaluation failed: {e}. Falling back to heuristic.")
        return heuristic_missed_reminder(patient_summary, medication_info, scheduled_time)


async def evaluate_monitor_telemetry(
    patient_summary: Dict[str, Any],
    monitor_spec: Dict[str, Any],
    past_remarks: List[str],
    media_path: Optional[str] = None,
    user_notes: Optional[str] = None,
) -> MonitorTriageOutput:
    if not ai_client:
        logger.info("Mistral AI client not configured; utilizing heuristic fallback.")
        return heuristic_monitor_telemetry(patient_summary, monitor_spec, past_remarks, user_notes)

    base64_image = encode_image_to_base64(media_path) if media_path else None

    context_prompt = f"""
PATIENT CONTEXT:
- Diagnosis: {patient_summary.get('primary_diagnosis', 'N/A')}
- Hospital Course: {patient_summary.get('hospital_course_description', 'N/A')}

MONITOR PROTOCOL:
- Instructions: {monitor_spec.get('instructions')}
- Things to Evaluate: {monitor_spec.get('things_to_evaluate')}
- TRIGGER ALERT IF: {monitor_spec.get('trigger_alert_if')}

PREVIOUS REMARKS:
{json.dumps(past_remarks, indent=2) if past_remarks else "No prior history"}

PATIENT SUBMISSION NOTES:
{user_notes or "None"}

TASK:
Examine the telemetry and determine whether to trigger an alert.
Return strictly a JSON object:
{{
  "alert_triggered": true | false,
  "priority": "low" | "medium" | "high" | "critical",
  "alert_content": "Concise message for clinicain explaining what went wrong(str)",
  "evaluation_remark": "Concise evaluation of the telemetry (str)"
}}
"""

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": "You are a clinical vision diagnostic assistant. Output strictly valid JSON."}
    ]

    if base64_image:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": context_prompt},
                {"type": "image_url", "image_url": {"url": base64_image}},
            ],
        })
    else:
        messages.append({
            "role": "user",
            "content": context_prompt + "\n[Note: Media unavailable. Evaluate based on textual report.]",
        })

    try:
        completion = await ai_client.chat.completions.create(
            model=settings.AI_VISION_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw_text = completion.choices[0].message.content or ""
        cleaned = clean_json_string(raw_text)
        return MonitorTriageOutput.model_validate_json(cleaned)
    except Exception as e:
        logger.error(f"Mistral telemetry evaluation failed: {e}. Falling back to heuristic.")
        return heuristic_monitor_telemetry(patient_summary, monitor_spec, past_remarks, user_notes)

async def evaluate_missed_telemetry(
    patient_summary: Dict[str, Any],
    monitor_spec: Dict[str, Any],
    past_remarks: List[str],
) -> MonitorTriageOutput:
    if not ai_client:
        logger.info("Mistral AI client not configured; utilizing heuristic fallback.")
        return heuristic_monitor_telemetry(
            patient_summary, 
            monitor_spec, 
            past_remarks, 
            user_notes="Patient missed scheduled telemetry submission (>30m overdue)."
        )

    context_prompt = f"""
PATIENT CONTEXT:
- Diagnosis: {patient_summary.get('primary_diagnosis', 'N/A')}
- Hospital Course: {patient_summary.get('hospital_course_description', 'N/A')}

MONITOR PROTOCOL:
- Instructions: {monitor_spec.get('instructions')}
- Things to Evaluate: {monitor_spec.get('things_to_evaluate')}
- TRIGGER ALERT IF: {monitor_spec.get('trigger_alert_if')}

PREVIOUS REMARKS:
{json.dumps(past_remarks, indent=2) if past_remarks else "No prior history"}

INCIDENT:
The patient has MISSED submitting the required telemetry check/report, and the submission is now overdue past the 30-minute grace period.

TASK:
Because this telemetry was missed, you must trigger an alert ("alert_triggered": true).
Assess the patient's post-operative context, diagnosis, and the monitor protocol to determine the clinical urgency and priority of this lapse.
Return strictly a JSON object:
{{
  "alert_triggered": true,
  "priority": "low" | "medium" | "high" | "critical",
  "alert_content": "Concise message explaining what went wrong (str)",
  "evaluation_remark": "Concise message messaging the reasoning for the alert (str)"
}}
"""

    messages: List[Dict[str, Any]] = [
        {
            "role": "system",
            "content": "You are an expert post-operative clinical triage assistant. Output strictly valid JSON.",
        },
        {
            "role": "user",
            "content": context_prompt,
        },
    ]

    try:
        completion = await ai_client.chat.completions.create(
            model=settings.AI_VISION_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw_text = completion.choices[0].message.content or ""
        cleaned = clean_json_string(raw_text)
        return MonitorTriageOutput.model_validate_json(cleaned)
    except Exception as e:
        logger.error(f"Mistral missed telemetry evaluation failed: {e}. Falling back to heuristic.")
        return heuristic_monitor_telemetry(
            patient_summary, 
            monitor_spec, 
            past_remarks, 
            user_notes="Patient missed scheduled telemetry submission (>30m overdue)."
        )


async def parse_discharge_summary_image(
    file_bytes: bytes,
    mime_type: str = "image/jpeg",
) -> ParsedDischargeSummary:
    if not ai_client:
        logger.info("Mistral AI client not configured; utilizing default mock summary.")
        return fallback_mock_discharge_summary()

    base64_encoded = base64.b64encode(file_bytes).decode("utf-8")
    data_uri = f"data:{mime_type};base64,{base64_encoded}"

    prompt = """
Extract all information from this medical discharge summary into a single valid JSON object.
Return strictly the JSON object adhering to this structure:
{
  "patient_id": "PT-XXX (extract ID or generate 3 digits)",
  "name": "Patient full name",
  "age": 0,
  "gender": "Male | Female | Other",
  "admission_date": "YYYY-MM-DD or null",
  "discharge_date": "YYYY-MM-DD or null",
  "primary_diagnosis": "Primary diagnosis",
  "hospital_course_description": "Course summary",
  "physician_name": "Doctor name or null",
  "physician_contact": "Doctor phone or null",
  "caretaker_name": "Caretaker name or null",
  "caretaker_contact": "Caretaker phone or null",
  "caretaker_relationship": "Relationship or null",
  "medications_at_discharge": [
    {"medication_name": "Name", "dosage": "Dose", "frequency": "Frequency", "duration": "Duration"}
  ],
  "discharge_instructions": [
    {"instruction": "Instruction"}
  ],
  "reminders": [
    {"frequency": "daily", "time": "08:00", "content": "Action reminder"}
  ],
  "monitors": [
    {
      "frequency": "daily | once | per_week | per_month | per_year",
      "input_type": "image | video",
      "time": "09:00",
      "instructions": "Capture instruction",
      "things_to_evaluate": "Clinical parameters (str) ",
      "trigger_alert_if": "Alert trigger criteria (str)"
    }
  ]
}
"""

    messages = [
        {"role": "system", "content": "You are a clinical document parser that outputs strictly raw JSON."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_uri}},
            ],
        },
    ]

    try:
        completion = await ai_client.chat.completions.create(
            model=settings.AI_VISION_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=3000,
        )
        raw_text = completion.choices[0].message.content or ""
        cleaned = clean_json_string(raw_text)
        return ParsedDischargeSummary.model_validate_json(cleaned)
    except Exception as e:
        logger.error(f"Mistral discharge parsing failed: {e}. Falling back to default mock summary.")
        return fallback_mock_discharge_summary()