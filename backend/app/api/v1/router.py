from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import text, select, func, case

from app.db.session import get_db
from app.models.patient import Patient
from app.models.alert import Alert
from app.models.enums import AlertPriority
from app.services.scheduler import scheduler

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
