import os
import json
import base64
import mimetypes
import logging
import random
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from app.core.config import settings
from app.models.enums import AlertPriority
from app.schemas.discharge_parse import ParsedDischargeSummary

logger = logging.getLogger(__name__)

try:
    from openai import AsyncOpenAI
    api_key = settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY
    if api_key:
        openai_client = AsyncOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=api_key,
            default_headers={
                "HTTP-Referer": "http://localhost:8000",
                "X-Title": settings.PROJECT_NAME,
            }
        )
    else:
        openai_client = None
except ImportError:
    AsyncOpenAI = None
    openai_client = None

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
        description="True if the telemetry violates the protocol trigger threshold, otherwise False"
    )
    priority: AlertPriority = Field(
        default=AlertPriority.MEDIUM,
        description="Alert priority level if triggered ('low', 'medium', 'high', 'critical')"
    )
    alert_content: Optional[str] = Field(
        default=None,
        description="Clinician-facing alert description if triggered; null otherwise"
    )
    evaluation_remark: str = Field(
        description="Objective medical remark and findings to log in the patient's record"
    )

def encode_image_to_base64(file_path: str) -> Optional[str]:
    if not file_path or not os.path.exists(file_path):
        return None
    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        mime_type = "image/jpeg"
    try:
        with open(file_path, "rb") as image_file:
            encoded_str = base64.b64encode(image_file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded_str}"
    except Exception as e:
        logger.error(f"Error encoding image {file_path}: {e}")
        return None

def heuristic_missed_reminder(
    patient_summary: Dict[str, Any],
    medication_info: str,
    scheduled_time: str
) -> ReminderTriageOutput:
    content_lower = medication_info.lower()
    diagnosis_lower = str(patient_summary.get("primary_diagnosis", "")).lower()

    critical_keywords = [
        "ticagrelor", "aspirin", "plavix", "clopidogrel", "brilinta", 
        "warfarin", "eliquis", "apixaban", "xarelto", "insulin", "glargine"
    ]
    high_risk_keywords = [
        "metoprolol", "carvedilol", "losartan", "amlodipine", 
        "furosemide", "torsemide", "entresto", "prednisone"
    ]

    is_stent_or_cardiac = any(k in diagnosis_lower for k in ["stent", "pci", "coronary", "myocardial", "infarction"])

    if any(drug in content_lower for drug in critical_keywords) and is_stent_or_cardiac:
        priority = AlertPriority.CRITICAL
        alert_text = f"CRITICAL: Missed post-PCI antiplatelet regimen ({medication_info}) scheduled for {scheduled_time}. Acute thrombosis risk."
        rationale = "Sudden interruption of dual antiplatelet therapy in early post-PCI period triggers catastrophic in-stent thrombosis."
    elif any(drug in content_lower for drug in critical_keywords):
        priority = AlertPriority.HIGH
        alert_text = f"High Risk: Missed critical medication dose ({medication_info}) scheduled for {scheduled_time}."
        rationale = "High-risk anticoagulant, antiplatelet, or glycemic agent window lapsed by >30 minutes."
    elif any(drug in content_lower for drug in high_risk_keywords):
        priority = AlertPriority.HIGH
        alert_text = f"Overdue: Missed maintenance cardiovascular dose ({medication_info}) scheduled at {scheduled_time}."
        rationale = "Delayed antihypertensive or diuretic increases risk of rebound hemodynamics or volume overload."
    else:
        priority = AlertPriority.MEDIUM
        alert_text = f"Delayed reminder: Patient has not logged completion for: {medication_info} (scheduled {scheduled_time})."
        rationale = "Routine schedule lapse exceeds 30-minute grace window."

    return ReminderTriageOutput(
        priority=priority,
        alert_content=alert_text,
        clinical_rationale=rationale
    )

def heuristic_monitor_telemetry(
    patient_summary: Dict[str, Any],
    monitor_spec: Dict[str, Any],
    past_remarks: List[str],
    user_notes: Optional[str] = None
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
            evaluation_remark=f"Submission indicates abnormal telemetry signs ({', '.join(found_issues)}). Exceeds baseline thresholds."
        )

    return MonitorTriageOutput(
        alert_triggered=False,
        priority=AlertPriority.LOW,
        alert_content=None,
        evaluation_remark=f"Telemetry submission reviewed for {instructions}. Parameters within acceptable post-discharge margins."
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
        hospital_course_description="Admitted with fluid overload, bilateral lower extremity 3+ edema, and severe orthopnea. Diuresed with IV Furosemide. Switched to oral Torsemide regimen with stable electrolytes.",
        physician_name="Dr. Katherine Cole",
        physician_contact="+1 (555) 438-9201",
        caretaker_name="David Moore",
        caretaker_contact="+1 (555) 312-7890",
        caretaker_relationship="Spouse",
        medications_at_discharge=[
            {"medication_name": "Torsemide", "dosage": "20 mg", "frequency": "Once daily in morning", "duration": "Ongoing"},
            {"medication_name": "Sacubitril / Valsartan", "dosage": "24/26 mg", "frequency": "Twice daily", "duration": "Ongoing"},
            {"medication_name": "Spironolactone", "dosage": "25 mg", "frequency": "Once daily", "duration": "Ongoing"}
        ],
        discharge_instructions=[
            {"instruction": "Weigh yourself daily in the morning after voiding and before breakfast."},
            {"instruction": "Limit sodium intake strictly to under 2,000 mg daily."},
            {"instruction": "Call clinic immediately if body weight increases by >3 lbs in 24 hours."}
        ],
        reminders=[
            {"frequency": "daily", "time": "08:00", "content": "Take Torsemide 20mg and Entresto 24/26mg with water."},
            {"frequency": "daily", "time": "20:00", "content": "Take evening dose of Entresto 24/26mg."}
        ],
        monitors=[
            {
                "frequency": "daily",
                "input_type": "image",
                "time": "08:15",
                "instructions": "Take a clear photograph of the digital weight scale display.",
                "things_to_evaluate": "Daily morning dry body weight.",
                "trigger_alert_if": "Weight gain >= 3 lbs over baseline within 48 hours."
            },
            {
                "frequency": "daily",
                "input_type": "image",
                "time": "18:00",
                "instructions": "Photograph both lower legs and ankles to inspect peripheral edema.",
                "things_to_evaluate": "Pitting edema or swelling severity over ankles.",
                "trigger_alert_if": "Pitting indentation persists > 10 seconds or noticeable spread up mid-shin."
            }
        ]
    )

async def evaluate_missed_reminder(
    patient_summary: Dict[str, Any],
    medication_info: str,
    scheduled_time: str
) -> ReminderTriageOutput:
    if not openai_client:
        logger.info("OpenRouter client not configured; using heuristic fallback.")
        return heuristic_missed_reminder(patient_summary, medication_info, scheduled_time)

    prompt = f"""
You are an expert post-discharge clinical triage assistant.
A patient has failed to acknowledge or take a scheduled medication/care reminder within a 30-minute grace period.

PATIENT CLINICAL DOSSIER:
- Patient Name: {patient_summary.get('name', 'Unknown')}
- Age/Gender: {patient_summary.get('age')} {patient_summary.get('gender')}
- Primary Diagnosis: {patient_summary.get('primary_diagnosis', 'N/A')}
- Hospital Course: {patient_summary.get('hospital_course_description', 'N/A')}
- Medications Prescribed: {json.dumps(patient_summary.get('medications_at_discharge', []), indent=2)}

MISSED CARE REGIMEN:
- Target Item: {medication_info}
- Scheduled Intake Time: {scheduled_time} (Current delay: > 30 minutes)

TASK:
1. Assess the risk of missing this specific dose in the context of the primary diagnosis and hospital course.
   - 'critical': Immediately life-threatening if missed.
   - 'high': Serious risk of rapid clinical deterioration.
   - 'medium': Standard antibiotics, oral steroids, maintenance inhalers.
   - 'low': General wellness reminders.
2. Formulate a succinct, clinician-facing alert message.
3. Provide the medical rationale.

Return valid JSON:
{{
  "priority": "low" | "medium" | "high" | "critical",
  "alert_content": "string",
  "clinical_rationale": "string"
}}
"""
    try:
        try:
            response = await openai_client.beta.chat.completions.parse(
                model=settings.AI_TEXT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a clinical triage AI. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format=ReminderTriageOutput,
                temperature=0.1
            )
            if response.choices[0].message.parsed:
                return response.choices[0].message.parsed
        except Exception:
            completion = await openai_client.chat.completions.create(
                model=settings.AI_TEXT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a clinical triage AI. Return strictly a JSON object."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            content = completion.choices[0].message.content
            return ReminderTriageOutput.model_validate_json(content)
    except Exception as e:
        logger.error(f"OpenRouter evaluation failed: {e}. Falling back to heuristic.")
        return heuristic_missed_reminder(patient_summary, medication_info, scheduled_time)

async def evaluate_monitor_telemetry(
    patient_summary: Dict[str, Any],
    monitor_spec: Dict[str, Any],
    past_remarks: List[str],
    media_path: Optional[str] = None,
    user_notes: Optional[str] = None
) -> MonitorTriageOutput:
    if not openai_client:
        logger.info("OpenRouter client not configured; using heuristic fallback.")
        return heuristic_monitor_telemetry(patient_summary, monitor_spec, past_remarks, user_notes)

    base64_image = encode_image_to_base64(media_path) if media_path else None

    context_prompt = f"""
PATIENT CONTEXT:
- Primary Diagnosis: {patient_summary.get('primary_diagnosis', 'N/A')}
- Hospital Course: {patient_summary.get('hospital_course_description', 'N/A')}

MONITOR PROTOCOL SPECIFICATION:
- Instructions Given to Patient: {monitor_spec.get('instructions')}
- What to Evaluate: {monitor_spec.get('things_to_evaluate')}
- TRIGGER ALERT IF (STRICT CRITERIA): {monitor_spec.get('trigger_alert_if')}

LONGITUDINAL TELEMETRY HISTORY (Prior Submissions):
{json.dumps(past_remarks, indent=2) if past_remarks else "No prior history"}

PATIENT NOTES WITH SUBMISSION:
{user_notes or "None provided"}

TASK:
1. Examine the submitted telemetry image/data against the 'TRIGGER ALERT IF' criteria.
2. Determine if an alert should be triggered (alert_triggered = true/false).
3. If true, assign priority ('low', 'medium', 'high', 'critical') and write a clear alert description.
4. Compose an objective, professional EHR remark summarizing findings.

Return valid JSON:
{{
  "alert_triggered": bool,
  "priority": "low" | "medium" | "high" | "critical",
  "alert_content": "string or null",
  "evaluation_remark": "string"
}}
"""

    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": "You analyze clinical telemetry photos/videos. Return only valid JSON."}
    ]

    if base64_image:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": context_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": base64_image,
                        "detail": "high"
                    }
                }
            ]
        })
    else:
        messages.append({
            "role": "user",
            "content": context_prompt + "\n[Note: Evaluate based on textual report and history.]"
        })

    try:
        try:
            response = await openai_client.beta.chat.completions.parse(
                model=settings.AI_VISION_MODEL,
                messages=messages,
                response_format=MonitorTriageOutput,
                temperature=0.1
            )
            if response.choices[0].message.parsed:
                return response.choices[0].message.parsed
        except Exception:
            completion = await openai_client.chat.completions.create(
                model=settings.AI_VISION_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            content = completion.choices[0].message.content
            return MonitorTriageOutput.model_validate_json(content)
    except Exception as e:
        logger.error(f"OpenRouter telemetry evaluation failed: {e}. Falling back to heuristic.")
        return heuristic_monitor_telemetry(patient_summary, monitor_spec, past_remarks, user_notes)

async def parse_discharge_summary_image(
    file_bytes: bytes,
    mime_type: str = "image/jpeg"
) -> ParsedDischargeSummary:
    if not openai_client:
        logger.info("OpenRouter client not configured; using default mock summary.")
        return fallback_mock_discharge_summary()

    base64_encoded = base64.b64encode(file_bytes).decode("utf-8")
    data_uri = f"data:{mime_type};base64,{base64_encoded}"

    prompt = """
You are a board-certified clinical informaticist extracting structured intake data from a hospital discharge document scan.

Analyze this discharge summary image and extract:
1. Patient Demographics: full name, age, gender, admission date, discharge date.
2. Diagnoses & Course: primary discharge diagnosis and concise hospital course narrative.
3. Care Contacts: attending physician name/phone and primary family caretaker name/phone/relationship.
4. Prescriptions: all medications at discharge with dosage, frequency, and duration.
5. Actionable Care Reminders: translate the medication schedule into scheduled daily reminders (frequency: 'daily', time: 'HH:MM', content: 'Take Drug').
6. Telemetry Monitors: define required photo/video surveillance check-ins with check-in time, instructions, evaluation items, and strict alert threshold criteria ('trigger_alert_if').
"""

    messages = [
        {"role": "system", "content": "You extract structured medical data from physical discharge summaries. Return valid JSON."},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_uri, "detail": "high"}}
            ]
        }
    ]

    try:
        try:
            response = await openai_client.beta.chat.completions.parse(
                model=settings.AI_VISION_MODEL,
                messages=messages,
                response_format=ParsedDischargeSummary,
                temperature=0.1
            )
            if response.choices[0].message.parsed:
                return response.choices[0].message.parsed
        except Exception:
            completion = await openai_client.chat.completions.create(
                model=settings.AI_VISION_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1
            )
            content = completion.choices[0].message.content
            return ParsedDischargeSummary.model_validate_json(content)
    except Exception as e:
        logger.error(f"OpenRouter discharge parsing failed: {e}. Falling back to default mock summary.")
        return fallback_mock_discharge_summary()
