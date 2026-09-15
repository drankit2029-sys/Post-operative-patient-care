from datetime import datetime, date, timezone
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import text, select, func, case

from app.db.session import get_db, SessionLocal
from app.models.patient import Patient
from app.models.alert import Alert
from app.models.reminder import Reminder
from app.models.monitor import Monitor
from app.models.events import PastReminderEvent, PastMonitorEvent
from app.models.enums import AlertPriority, ReminderFrequency, MonitorFrequency, InputType, TaskStatus
from app.services.scheduler import scheduler
from app.schemas.discharge_parse import ParsedDischargeSummary
from app.services.ai_evaluator import parse_discharge_summary_image
from app.models.task_instance import ReminderTaskInstance
from app.schemas.task_instance import (
    ReminderTaskInstanceResponse,
    ReminderTaskInstanceUpdate,
)
from app.services.state_machine import transition_task_status
from app.models.task_instance import MonitorTaskInstance
from app.schemas.task_instance import (
    MonitorTaskInstanceResponse,
    MonitorTaskInstanceUpdate,
)
from app.services.state_machine import transition_monitor_task_status

api_router = APIRouter(prefix="/v1")

class AlertFeedItem(BaseModel):
    id: str
    patientId: str
    patientName: str
    caretakerContact: str
    reminderId: Optional[int] = None
    monitorId: Optional[int] = None
    content: str
    priority: str
    timestamp: str

class PatientListItem(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    caretaker_no: str
    date_of_discharge: Optional[str] = None
    created_at: str
    final_diagnosis: Optional[str] = None
    recent_alert: Optional[AlertFeedItem] = None

class ReminderItem(BaseModel):
    id: Optional[int] = None
    frequency: str
    time: str
    content: str
    created_at: Optional[str] = None

class MonitorItem(BaseModel):
    id: Optional[int] = None
    frequency: str
    input_type: str
    time: str
    instructions: str
    things_to_evaluate: str
    trigger_alert_if: str
    created_at: Optional[str] = None

class PastReminderEventItem(BaseModel):
    id: int
    reminder_id: Optional[int] = None
    content: str
    resolved_or_not: bool
    created_at: str

class PastMonitorEventItem(BaseModel):
    id: int
    monitor_id: Optional[int] = None
    input_given: str
    remark: Optional[str] = None
    alert_triggered_or_not: bool
    created_at: str

class PatientRemindersResponse(BaseModel):
    patient_id: str
    patient_name: str
    reminders: List[ReminderItem]
    past_events: List[PastReminderEventItem]

class PatientMonitorsResponse(BaseModel):
    patient_id: str
    patient_name: str
    monitors: List[MonitorItem]
    past_events: List[PastMonitorEventItem]

class SingleReminderDetailResponse(BaseModel):
    reminder: Dict[str, Any]
    alerts: List[AlertFeedItem]
    past_events: List[PastReminderEventItem]

class SingleMonitorDetailResponse(BaseModel):
    monitor: Dict[str, Any]
    alerts: List[AlertFeedItem]
    past_events: List[PastMonitorEventItem]

class PatientDetailResponse(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    primary_diagnosis: Optional[str] = None
    hospital_course_description: Optional[str] = None
    treatment_summary: List[Dict[str, Any]] = Field(default_factory=list)
    medications_at_discharge: List[Dict[str, Any]] = Field(default_factory=list)
    discharge_instructions: List[Dict[str, Any]] = Field(default_factory=list)
    follow_up_appointments: List[Dict[str, Any]] = Field(default_factory=list)
    responsible_physician: Dict[str, Any] = Field(default_factory=dict)
    caretaker: Dict[str, Any] = Field(default_factory=dict)
    additional_notes: List[Dict[str, Any]] = Field(default_factory=list)
    reminders: List[ReminderItem] = Field(default_factory=list)
    monitors: List[MonitorItem] = Field(default_factory=list)
    alerts: List[AlertFeedItem] = Field(default_factory=list)


class ReminderCreateItem(BaseModel):
    frequency: str = "daily"
    time: str
    content: str

class MonitorCreateItem(BaseModel):
    frequency: str = "daily"
    input_type: str = "image"
    time: str
    instructions: str
    things_to_evaluate: str
    trigger_alert_if: str

class PatientCreatePayload(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    primary_diagnosis: str
    hospital_course_description: Optional[str] = ""
    treatment_summary: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    medications_at_discharge: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    discharge_instructions: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    follow_up_appointments: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    responsible_physician: Optional[Dict[str, Any]] = Field(default_factory=dict)
    additional_notes: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    caretaker: Optional[Dict[str, Any]] = Field(default_factory=dict)
    reminders: Optional[List[ReminderCreateItem]] = Field(default_factory=list)
    monitors: Optional[List[MonitorCreateItem]] = Field(default_factory=list)

class PatientUpdatePayload(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    primary_diagnosis: Optional[str] = None
    hospital_course_description: Optional[str] = None
    treatment_summary: Optional[List[Dict[str, Any]]] = None
    medications_at_discharge: Optional[List[Dict[str, Any]]] = None
    discharge_instructions: Optional[List[Dict[str, Any]]] = None
    follow_up_appointments: Optional[List[Dict[str, Any]]] = None
    responsible_physician: Optional[Dict[str, Any]] = None
    caretaker: Optional[Dict[str, Any]] = None
    additional_notes: Optional[List[Dict[str, Any]]] = None
    reminders: Optional[List[ReminderItem]] = None
    monitors: Optional[List[MonitorItem]] = None


class PatientTodayTasksResponse(BaseModel):
    patient_id: str
    patient_name: str
    date: str
    reminders: List[Dict[str, Any]]
    monitors: List[Dict[str, Any]]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

      
def format_relative_time(dt: datetime) -> str:
    if not dt:
        return ""
    now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.utcnow()
    seconds = max(0, int((now - dt).total_seconds()))
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"

def parse_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        return None

def serialize_patient_detail(patient: Patient) -> PatientDetailResponse:
    caretaker_info = patient.caretaker or {}
    caretaker_contact = caretaker_info.get("contact", "N/A")

    sorted_alerts = sorted(
        patient.alerts or [],
        key=lambda a: (
            4 if a.priority == AlertPriority.CRITICAL else
            3 if a.priority == AlertPriority.HIGH else
            2 if a.priority == AlertPriority.MEDIUM else 1,
            a.created_at
        ),
        reverse=True
    )

    formatted_alerts = [
        AlertFeedItem(
            id=f"ALT-{alert.id:03d}",
            patientId=patient.patient_id,
            patientName=patient.name,
            caretakerContact=caretaker_contact,
            reminderId=alert.reminder_id,
            monitorId=alert.monitor_id,
            content=alert.content,
            priority=alert.priority.value if hasattr(alert.priority, "value") else str(alert.priority),
            timestamp=format_relative_time(alert.created_at)
        )
        for alert in sorted_alerts
    ]

    formatted_reminders = [
        ReminderItem(
            id=rem.id,
            frequency=rem.frequency.value if hasattr(rem.frequency, "value") else str(rem.frequency),
            time=rem.time,
            content=rem.content,
            created_at=rem.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if rem.created_at else None
        )
        for rem in (patient.reminders or [])
    ]

    formatted_monitors = [
        MonitorItem(
            id=mon.id,
            frequency=mon.frequency.value if hasattr(mon.frequency, "value") else str(mon.frequency),
            input_type=mon.input_type.value if hasattr(mon.input_type, "value") else str(mon.input_type),
            time=mon.time,
            instructions=mon.instructions,
            things_to_evaluate=mon.things_to_evaluate,
            trigger_alert_if=mon.trigger_alert_if,
            created_at=mon.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if mon.created_at else None
        )
        for mon in (patient.monitors or [])
    ]

    return PatientDetailResponse(
        patient_id=patient.patient_id,
        name=patient.name,
        age=patient.age,
        gender=patient.gender,
        admission_date=patient.admission_date.strftime("%Y-%m-%d") if patient.admission_date else None,
        discharge_date=patient.discharge_date.strftime("%Y-%m-%d") if patient.discharge_date else None,
        primary_diagnosis=patient.primary_diagnosis or "",
        hospital_course_description=patient.hospital_course_description or "",
        treatment_summary=patient.treatment_summary or [],
        medications_at_discharge=patient.medications_at_discharge or [],
        discharge_instructions=patient.discharge_instructions or [],
        follow_up_appointments=patient.follow_up_appointments or [],
        responsible_physician=patient.responsible_physician or {},
        caretaker=patient.caretaker or {},
        additional_notes=patient.additional_notes or [],
        reminders=formatted_reminders,
        monitors=formatted_monitors,
        alerts=formatted_alerts
    )

@api_router.get("/health")
def health_check(db: Session = Depends(get_db)):
    journal_mode = db.execute(text("PRAGMA journal_mode;")).scalar()
    return {
        "status": "healthy",
        "database": {
            "connected": True,
            "journal_mode": journal_mode
        },
        "scheduler_running": scheduler.running
    }

@api_router.get("/patients/count")
def get_patient_count(db: Session = Depends(get_db)):
    count = db.scalar(select(func.count()).select_from(Patient)) or 0
    return {"count": count}

@api_router.get("/alerts", response_model=List[AlertFeedItem])
def get_alerts(
    limit: Optional[int] = Query(None, ge=1),
    patient_id: Optional[str] = Query(None),
    reminder_id: Optional[int] = Query(None),
    monitor_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    priority_order = case(
        (Alert.priority == AlertPriority.CRITICAL, 4),
        (Alert.priority == AlertPriority.HIGH, 3),
        (Alert.priority == AlertPriority.MEDIUM, 2),
        (Alert.priority == AlertPriority.LOW, 1),
        else_=0
    )

    query = (
        select(Alert, Patient)
        .join(Patient, Alert.patient_id == Patient.patient_id)
        .order_by(priority_order.desc(), Alert.created_at.desc())
    )

    if patient_id:
        query = query.where(Alert.patient_id == patient_id)
    if reminder_id:
        query = query.where(Alert.reminder_id == reminder_id)
    if monitor_id:
        query = query.where(Alert.monitor_id == monitor_id)
    if limit is not None:
        query = query.limit(limit)

    results = db.execute(query).all()

    formatted_alerts = []
    for alert, patient in results:
        caretaker_info = patient.caretaker or {}
        caretaker_contact = caretaker_info.get("contact", "N/A")

        formatted_alerts.append(
            AlertFeedItem(
                id=f"ALT-{alert.id:03d}",
                patientId=patient.patient_id,
                patientName=patient.name,
                caretakerContact=caretaker_contact,
                reminderId=alert.reminder_id,
                monitorId=alert.monitor_id,
                content=alert.content,
                priority=alert.priority.value if hasattr(alert.priority, "value") else str(alert.priority),
                timestamp=format_relative_time(alert.created_at)
            )
        )

    return formatted_alerts

@api_router.get("/patients", response_model=List[PatientListItem])
def get_patients_list(db: Session = Depends(get_db)):
    query = (
        select(Patient)
        .options(selectinload(Patient.alerts))
        .order_by(Patient.created_at.desc())
    )
    patients = db.scalars(query).all()

    response = []
    for patient in patients:
        caretaker_dict = patient.caretaker or {}
        caretaker_contact = caretaker_dict.get("contact", "N/A")

        recent_alert = None
        if patient.alerts:
            latest_alert = max(patient.alerts, key=lambda a: a.created_at)
            recent_alert = AlertFeedItem(
                id=f"ALT-{latest_alert.id:03d}",
                patientId=patient.patient_id,
                patientName=patient.name,
                caretakerContact=caretaker_contact,
                reminderId=latest_alert.reminder_id,
                monitorId=latest_alert.monitor_id,
                content=latest_alert.content,
                priority=latest_alert.priority.value if hasattr(latest_alert.priority, "value") else str(latest_alert.priority),
                timestamp=format_relative_time(latest_alert.created_at)
            )

        discharge_str = patient.discharge_date.strftime("%Y-%m-%d") if patient.discharge_date else None
        created_str = patient.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if patient.created_at else ""

        response.append(
            PatientListItem(
                patient_id=patient.patient_id,
                name=patient.name,
                age=patient.age,
                gender=patient.gender,
                caretaker_no=caretaker_contact,
                date_of_discharge=discharge_str,
                created_at=created_str,
                final_diagnosis=patient.primary_diagnosis or "N/A",
                recent_alert=recent_alert
            )
        )

    return response

@api_router.get("/patients/{patient_id}", response_model=PatientDetailResponse)
def get_patient_detail(patient_id: str, db: Session = Depends(get_db)):
    query = (
        select(Patient)
        .options(
            selectinload(Patient.alerts),
            selectinload(Patient.reminders),
            selectinload(Patient.monitors),
        )
        .where(Patient.patient_id == patient_id)
    )
    patient = db.scalar(query)

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{patient_id}' not found."
        )

    return serialize_patient_detail(patient)

@api_router.put("/patients/{patient_id}", response_model=PatientDetailResponse)
def update_patient_detail(
    patient_id: str,
    payload: PatientUpdatePayload,
    db: Session = Depends(get_db)
):
    query = (
        select(Patient)
        .options(
            selectinload(Patient.alerts),
            selectinload(Patient.reminders),
            selectinload(Patient.monitors),
        )
        .where(Patient.patient_id == patient_id)
    )
    patient = db.scalar(query)

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{patient_id}' not found."
        )

    if payload.name is not None:
        patient.name = payload.name
    if payload.age is not None:
        patient.age = payload.age
    if payload.gender is not None:
        patient.gender = payload.gender
    if payload.admission_date is not None:
        patient.admission_date = parse_date(payload.admission_date)
    if payload.discharge_date is not None:
        patient.discharge_date = parse_date(payload.discharge_date)
    if payload.primary_diagnosis is not None:
        patient.primary_diagnosis = payload.primary_diagnosis
    if payload.hospital_course_description is not None:
        patient.hospital_course_description = payload.hospital_course_description

    if payload.treatment_summary is not None:
        patient.treatment_summary = payload.treatment_summary
    if payload.medications_at_discharge is not None:
        patient.medications_at_discharge = payload.medications_at_discharge
    if payload.discharge_instructions is not None:
        patient.discharge_instructions = payload.discharge_instructions
    if payload.follow_up_appointments is not None:
        patient.follow_up_appointments = payload.follow_up_appointments
    if payload.responsible_physician is not None:
        patient.responsible_physician = payload.responsible_physician
    if payload.caretaker is not None:
        patient.caretaker = payload.caretaker
    if payload.additional_notes is not None:
        patient.additional_notes = payload.additional_notes

    if payload.reminders is not None:
        existing_reminders = {r.id: r for r in patient.reminders}
        kept_reminder_ids = set()

        for rem_item in payload.reminders:
            freq_val = ReminderFrequency(rem_item.frequency.lower()) if rem_item.frequency else ReminderFrequency.DAILY

            if rem_item.id and rem_item.id in existing_reminders:
                existing_rem = existing_reminders[rem_item.id]
                existing_rem.frequency = freq_val
                existing_rem.time = rem_item.time
                existing_rem.content = rem_item.content
                kept_reminder_ids.add(rem_item.id)
            else:
                new_rem = Reminder(
                    patient_id=patient.patient_id,
                    frequency=freq_val,
                    time=rem_item.time,
                    content=rem_item.content
                )
                db.add(new_rem)

        for rem_id, rem_obj in existing_reminders.items():
            if rem_id not in kept_reminder_ids:
                db.delete(rem_obj)

    if payload.monitors is not None:
        existing_monitors = {m.id: m for m in patient.monitors}
        kept_monitor_ids = set()

        for mon_item in payload.monitors:
            freq_val = MonitorFrequency(mon_item.frequency.lower()) if mon_item.frequency else MonitorFrequency.DAILY
            input_val = InputType(mon_item.input_type.lower()) if mon_item.input_type else InputType.IMAGE

            if mon_item.id and mon_item.id in existing_monitors:
                existing_mon = existing_monitors[mon_item.id]
                existing_mon.frequency = freq_val
                existing_mon.input_type = input_val
                existing_mon.time = mon_item.time
                existing_mon.instructions = mon_item.instructions
                existing_mon.things_to_evaluate = mon_item.things_to_evaluate
                existing_mon.trigger_alert_if = mon_item.trigger_alert_if
                kept_monitor_ids.add(mon_item.id)
            else:
                new_mon = Monitor(
                    patient_id=patient.patient_id,
                    frequency=freq_val,
                    input_type=input_val,
                    time=mon_item.time,
                    instructions=mon_item.instructions,
                    things_to_evaluate=mon_item.things_to_evaluate,
                    trigger_alert_if=mon_item.trigger_alert_if
                )
                db.add(new_mon)

        for mon_id, mon_obj in existing_monitors.items():
            if mon_id not in kept_monitor_ids:
                db.delete(mon_obj)

    db.commit()
    db.refresh(patient)
    return serialize_patient_detail(patient)

@api_router.delete("/patients/{patient_id}")
def delete_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = db.scalar(select(Patient).where(Patient.patient_id == patient_id))
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID '{patient_id}' not found."
        )

    db.delete(patient)
    db.commit()
    return {"message": f"Patient '{patient_id}' deleted successfully."}

@api_router.get("/patients/{patient_id}/reminders", response_model=PatientRemindersResponse)
def get_patient_reminders_page(patient_id: str, db: Session = Depends(get_db)):
    patient = db.scalar(
        select(Patient)
        .options(
            selectinload(Patient.reminders),
            selectinload(Patient.past_reminder_events)
        )
        .where(Patient.patient_id == patient_id)
    )
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found.")

    formatted_reminders = [
        ReminderItem(
            id=rem.id,
            frequency=rem.frequency.value if hasattr(rem.frequency, "value") else str(rem.frequency),
            time=rem.time,
            content=rem.content,
            created_at=rem.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if rem.created_at else None
        )
        for rem in (patient.reminders or [])
    ]

    sorted_past_events = sorted(patient.past_reminder_events or [], key=lambda e: e.created_at, reverse=True)
    formatted_events = [
        PastReminderEventItem(
            id=e.id,
            reminder_id=e.reminder_id,
            content=e.content,
            resolved_or_not=e.resolved_or_not,
            created_at=e.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if e.created_at else ""
        )
        for e in sorted_past_events
    ]

    return PatientRemindersResponse(
        patient_id=patient.patient_id,
        patient_name=patient.name,
        reminders=formatted_reminders,
        past_events=formatted_events
    )

@api_router.get("/patients/{patient_id}/reminders/{reminder_id}", response_model=SingleReminderDetailResponse)
def get_single_reminder_detail(patient_id: str, reminder_id: int, db: Session = Depends(get_db)):
    patient = db.scalar(select(Patient).where(Patient.patient_id == patient_id))
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found.")

    reminder = db.scalar(
        select(Reminder)
        .where(Reminder.id == reminder_id, Reminder.patient_id == patient_id)
    )
    if not reminder:
        raise HTTPException(status_code=404, detail=f"Reminder #{reminder_id} not found for patient '{patient_id}'.")

    alerts = db.scalars(
        select(Alert)
        .where(Alert.patient_id == patient_id, Alert.reminder_id == reminder_id)
        .order_by(Alert.created_at.desc())
    ).all()

    caretaker_info = patient.caretaker or {}
    caretaker_contact = caretaker_info.get("contact", "N/A")

    formatted_alerts = [
        AlertFeedItem(
            id=f"ALT-{a.id:03d}",
            patientId=patient.patient_id,
            patientName=patient.name,
            caretakerContact=caretaker_contact,
            reminderId=a.reminder_id,
            monitorId=a.monitor_id,
            content=a.content,
            priority=a.priority.value if hasattr(a.priority, "value") else str(a.priority),
            timestamp=format_relative_time(a.created_at)
        )
        for a in alerts
    ]

    past_events = db.scalars(
        select(PastReminderEvent)
        .where(PastReminderEvent.patient_id == patient_id, PastReminderEvent.reminder_id == reminder_id)
        .order_by(PastReminderEvent.created_at.desc())
    ).all()

    formatted_events = [
        PastReminderEventItem(
            id=e.id,
            reminder_id=e.reminder_id,
            content=e.content,
            resolved_or_not=e.resolved_or_not,
            created_at=e.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if e.created_at else ""
        )
        for e in past_events
    ]

    return SingleReminderDetailResponse(
        reminder={
            "id": reminder.id,
            "patient_id": patient.patient_id,
            "patient_name": patient.name,
            "frequency": reminder.frequency.value if hasattr(reminder.frequency, "value") else str(reminder.frequency),
            "time": reminder.time,
            "content": reminder.content,
            "created_at": reminder.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if reminder.created_at else None
        },
        alerts=formatted_alerts,
        past_events=formatted_events
    )

@api_router.get("/patients/{patient_id}/monitors", response_model=PatientMonitorsResponse)
def get_patient_monitors_page(patient_id: str, db: Session = Depends(get_db)):
    patient = db.scalar(
        select(Patient)
        .options(
            selectinload(Patient.monitors),
            selectinload(Patient.past_monitor_events)
        )
        .where(Patient.patient_id == patient_id)
    )
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found.")

    formatted_monitors = [
        MonitorItem(
            id=mon.id,
            frequency=mon.frequency.value if hasattr(mon.frequency, "value") else str(mon.frequency),
            input_type=mon.input_type.value if hasattr(mon.input_type, "value") else str(mon.input_type),
            time=mon.time,
            instructions=mon.instructions,
            things_to_evaluate=mon.things_to_evaluate,
            trigger_alert_if=mon.trigger_alert_if,
            created_at=mon.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if mon.created_at else None
        )
        for mon in (patient.monitors or [])
    ]

    sorted_past_events = sorted(patient.past_monitor_events or [], key=lambda e: e.created_at, reverse=True)
    formatted_events = [
        PastMonitorEventItem(
            id=e.id,
            monitor_id=e.monitor_id,
            input_given=e.input_given,
            remark=e.remark,
            alert_triggered_or_not=e.alert_triggered_or_not,
            created_at=e.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if e.created_at else ""
        )
        for e in sorted_past_events
    ]

    return PatientMonitorsResponse(
        patient_id=patient.patient_id,
        patient_name=patient.name,
        monitors=formatted_monitors,
        past_events=formatted_events
    )

@api_router.get("/patients/{patient_id}/monitors/{monitor_id}", response_model=SingleMonitorDetailResponse)
def get_single_monitor_detail(patient_id: str, monitor_id: int, db: Session = Depends(get_db)):
    patient = db.scalar(select(Patient).where(Patient.patient_id == patient_id))
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found.")

    monitor = db.scalar(
        select(Monitor)
        .where(Monitor.id == monitor_id, Monitor.patient_id == patient_id)
    )
    if not monitor:
        raise HTTPException(status_code=404, detail=f"Monitor #{monitor_id} not found for patient '{patient_id}'.")

    alerts = db.scalars(
        select(Alert)
        .where(Alert.patient_id == patient_id, Alert.monitor_id == monitor_id)
        .order_by(Alert.created_at.desc())
    ).all()

    caretaker_info = patient.caretaker or {}
    caretaker_contact = caretaker_info.get("contact", "N/A")

    formatted_alerts = [
        AlertFeedItem(
            id=f"ALT-{a.id:03d}",
            patientId=patient.patient_id,
            patientName=patient.name,
            caretakerContact=caretaker_contact,
            reminderId=a.reminder_id,
            monitorId=a.monitor_id,
            content=a.content,
            priority=a.priority.value if hasattr(a.priority, "value") else str(a.priority),
            timestamp=format_relative_time(a.created_at)
        )
        for a in alerts
    ]

    past_events = db.scalars(
        select(PastMonitorEvent)
        .where(PastMonitorEvent.patient_id == patient_id, PastMonitorEvent.monitor_id == monitor_id)
        .order_by(PastMonitorEvent.created_at.desc())
    ).all()

    formatted_events = [
        PastMonitorEventItem(
            id=e.id,
            monitor_id=e.monitor_id,
            input_given=e.input_given,
            remark=e.remark,
            alert_triggered_or_not=e.alert_triggered_or_not,
            created_at=e.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if e.created_at else ""
        )
        for e in past_events
    ]

    return SingleMonitorDetailResponse(
        monitor={
            "id": monitor.id,
            "patient_id": patient.patient_id,
            "patient_name": patient.name,
            "frequency": monitor.frequency.value if hasattr(monitor.frequency, "value") else str(monitor.frequency),
            "input_type": monitor.input_type.value if hasattr(monitor.input_type, "value") else str(monitor.input_type),
            "time": monitor.time,
            "instructions": monitor.instructions,
            "things_to_evaluate": monitor.things_to_evaluate,
            "trigger_alert_if": monitor.trigger_alert_if,
            "created_at": monitor.created_at.strftime("%Y-%m-%dT%H:%M:%SZ") if monitor.created_at else None
        },
        alerts=formatted_alerts,
        past_events=formatted_events
    )

@api_router.post("/parse-discharge", response_model=ParsedDischargeSummary)
async def parse_discharge_summary(file: UploadFile = File(...)):
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/jpg", "application/pdf"]
    content_type = file.content_type or "image/jpeg"
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{content_type}'. Please upload PNG, JPG, or PDF."
        )
    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded file is empty.")
    return await parse_discharge_summary_image(file_bytes=file_bytes, mime_type=content_type)


@api_router.post("/patients", response_model=PatientDetailResponse, status_code=status.HTTP_201_CREATED)
def create_patient_record(
    payload: PatientCreatePayload,
    db: Session = Depends(get_db)
):
    existing = db.scalar(select(Patient).where(Patient.patient_id == payload.patient_id))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Patient with ID '{payload.patient_id}' already exists."
        )

    new_patient = Patient(
        patient_id=payload.patient_id,
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        admission_date=parse_date(payload.admission_date),
        discharge_date=parse_date(payload.discharge_date),
        primary_diagnosis=payload.primary_diagnosis,
        hospital_course_description=payload.hospital_course_description or "",
        treatment_summary=payload.treatment_summary or [],
        medications_at_discharge=payload.medications_at_discharge or [],
        discharge_instructions=payload.discharge_instructions or [],
        follow_up_appointments=payload.follow_up_appointments or [],
        responsible_physician=payload.responsible_physician or {},
        caretaker=payload.caretaker or {},
        additional_notes=payload.additional_notes or []
    )
    db.add(new_patient)
    db.flush()

    for rem in (payload.reminders or []):
        freq = ReminderFrequency(rem.frequency.lower()) if rem.frequency.lower() in [e.value for e in ReminderFrequency] else ReminderFrequency.DAILY
        db.add(Reminder(
            patient_id=new_patient.patient_id,
            frequency=freq,
            time=rem.time,
            content=rem.content
        ))

    for mon in (payload.monitors or []):
        freq = MonitorFrequency(mon.frequency.lower()) if mon.frequency.lower() in [e.value for e in MonitorFrequency] else MonitorFrequency.DAILY
        inp_type = InputType(mon.input_type.lower()) if mon.input_type.lower() in [e.value for e in InputType] else InputType.IMAGE
        db.add(Monitor(
            patient_id=new_patient.patient_id,
            frequency=freq,
            input_type=inp_type,
            time=mon.time,
            instructions=mon.instructions,
            things_to_evaluate=mon.things_to_evaluate,
            trigger_alert_if=mon.trigger_alert_if
        ))

    db.commit()

    created_patient = db.scalar(
        select(Patient)
        .options(
            selectinload(Patient.alerts),
            selectinload(Patient.reminders),
            selectinload(Patient.monitors),
        )
        .where(Patient.patient_id == new_patient.patient_id)
    )

    return serialize_patient_detail(created_patient)

# ... existing router setup ...

@api_router.put("/tasks/{task_id}", response_model=ReminderTaskInstanceResponse)
def update_task_instance(
    task_id: int,
    payload: ReminderTaskInstanceUpdate,
    db: Session = Depends(get_db),
):
    task = (
        db.query(ReminderTaskInstance)
        .options(joinedload(ReminderTaskInstance.reminder))
        .filter(ReminderTaskInstance.id == task_id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task instance {task_id} not found",
        )

    # Trigger audit event creation when transitioning to COMPLETED or MISSED
    if payload.status in [TaskStatus.COMPLETED, TaskStatus.MISSED] and task.status != payload.status:
        completion_time = payload.completed_at or datetime.now(timezone.utc)
        transition_task_status(
            db=db,
            task=task,
            new_status=payload.status,
            completion_time=completion_time,
        )
    else:
        task.status = payload.status
        if payload.completed_at:
            task.completed_at = payload.completed_at

    db.commit()
    db.refresh(task)
    return task

@api_router.put(
    "/monitor-tasks/{task_id}", response_model=MonitorTaskInstanceResponse
)
async def update_monitor_task_instance(
    task_id: int,
    payload: MonitorTaskInstanceUpdate,
    db: Session = Depends(get_db),
):
    task = (
        db.query(MonitorTaskInstance)
        .options(
            joinedload(MonitorTaskInstance.monitor),
            joinedload(MonitorTaskInstance.patient),
        )
        .filter(MonitorTaskInstance.id == task_id)
        .first()
    )
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Monitor task instance {task_id} not found",
        )

    # Trigger audit event creation and triage when transitioning to COMPLETED or MISSED
    if (
        payload.status in [TaskStatus.COMPLETED, TaskStatus.MISSED]
        and task.status != payload.status
    ):
        completion_time = payload.completed_at or datetime.now(timezone.utc)
        await transition_monitor_task_status(
            db=db,
            task=task,
            new_status=payload.status,
            completion_time=completion_time,
            input_given=payload.input_given,
            user_notes=payload.user_notes,
        )
    else:
        task.status = payload.status
        if payload.completed_at:
            task.completed_at = payload.completed_at
        if payload.input_given is not None:
            task.input_given = payload.input_given
        if payload.user_notes is not None:
            task.user_notes = payload.user_notes

    db.commit()
    db.refresh(task)
    return task



@api_router.get("/patients/{patient_id}/tasks/today", response_model=PatientTodayTasksResponse)
def get_patient_today_tasks(patient_id: str, db: Session = Depends(get_db)):
    patient = db.scalar(
        select(Patient)
        .options(selectinload(Patient.reminders), selectinload(Patient.monitors))
        .where(Patient.patient_id == patient_id)
    )
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found")

    today = date.today()

    # 1. On-demand ensure ReminderTaskInstances exist for today
    for rem in patient.reminders:
        existing_rem = db.scalar(
            select(ReminderTaskInstance).where(
                ReminderTaskInstance.reminder_id == rem.id,
                ReminderTaskInstance.scheduled_date == today
            )
        )
        if not existing_rem:
            db.add(ReminderTaskInstance(
                reminder_id=rem.id,
                patient_id=patient.patient_id,
                scheduled_date=today,
                scheduled_time=rem.time,
                status=TaskStatus.PENDING
            ))

    # 2. On-demand ensure MonitorTaskInstances exist for today
    for mon in patient.monitors:
        existing_mon = db.scalar(
            select(MonitorTaskInstance).where(
                MonitorTaskInstance.monitor_id == mon.id,
                MonitorTaskInstance.scheduled_date == today
            )
        )
        if not existing_mon:
            db.add(MonitorTaskInstance(
                monitor_id=mon.id,
                patient_id=patient.patient_id,
                scheduled_date=today,
                scheduled_time=mon.time,
                status=TaskStatus.PENDING
            ))

    db.commit()

    # 3. Retrieve populated tasks with relations
    reminder_tasks = db.scalars(
        select(ReminderTaskInstance)
        .options(joinedload(ReminderTaskInstance.reminder))
        .where(ReminderTaskInstance.patient_id == patient_id, ReminderTaskInstance.scheduled_date == today)
        .order_by(ReminderTaskInstance.scheduled_time.asc())
    ).all()

    monitor_tasks = db.scalars(
        select(MonitorTaskInstance)
        .options(joinedload(MonitorTaskInstance.monitor))
        .where(MonitorTaskInstance.patient_id == patient_id, MonitorTaskInstance.scheduled_date == today)
        .order_by(MonitorTaskInstance.scheduled_time.asc())
    ).all()

    formatted_reminders = [
        {
            "task_id": t.id,
            "reminder_id": t.reminder_id,
            "time": t.scheduled_time,
            "content": t.reminder.content if t.reminder else "Medication Dose",
            "frequency": t.reminder.frequency.value if t.reminder else "daily",
            "status": t.status.value,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
        }
        for t in reminder_tasks
    ]

    formatted_monitors = [
        {
            "task_id": t.id,
            "monitor_id": t.monitor_id,
            "time": t.scheduled_time,
            "instructions": t.monitor.instructions if t.monitor else "Telemetry check",
            "things_to_evaluate": t.monitor.things_to_evaluate if t.monitor else "",
            "trigger_alert_if": t.monitor.trigger_alert_if if t.monitor else "",
            "input_type": t.monitor.input_type.value if t.monitor else "image",
            "status": t.status.value,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "input_given": t.input_given,
            "user_notes": t.user_notes,
        }
        for t in monitor_tasks
    ]

    return PatientTodayTasksResponse(
        patient_id=patient.patient_id,
        patient_name=patient.name,
        date=today.isoformat(),
        reminders=formatted_reminders,
        monitors=formatted_monitors,
    )