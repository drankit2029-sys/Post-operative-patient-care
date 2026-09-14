from transitions import Machine
from enum import Enum
import logging
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app.models.enums import TaskStatus, AlertPriority
from app.models.events import PastReminderEvent, PastMonitorEvent
from app.models.task_instance import ReminderTaskInstance, MonitorTaskInstance
from typing import Optional
from app.models.alert import Alert
from app.models.task_instance import MonitorTaskInstance
from app.services.ai_evaluator import (
    evaluate_missed_telemetry,
    evaluate_monitor_telemetry,
    MonitorTriageOutput
)

logger = logging.getLogger(__name__)

class GenericState(str, Enum):
    IDLE = "idle"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"

class WorkflowStateMachine:
    def __init__(self, initial_state: GenericState = GenericState.IDLE):
        self.state = initial_state.value
        self.machine = Machine(
            model=self,
            states=[s.value for s in GenericState],
            initial=self.state,
            auto_transitions=False
        )
        self._register_transitions()

    def _register_transitions(self):
        self.machine.add_transition(
            trigger="activate", 
            source=GenericState.IDLE.value, 
            dest=GenericState.ACTIVE.value,
            after="on_enter_active"
        )
        self.machine.add_transition(
            trigger="suspend", 
            source=GenericState.ACTIVE.value, 
            dest=GenericState.SUSPENDED.value
        )
        self.machine.add_transition(
            trigger="resume", 
            source=GenericState.SUSPENDED.value, 
            dest=GenericState.ACTIVE.value
        )
        self.machine.add_transition(
            trigger="finish", 
            source=[GenericState.ACTIVE.value, GenericState.SUSPENDED.value], 
            dest=GenericState.COMPLETED.value
        )

    def on_enter_active(self):
        logger.info(f"FSM transitioned to {self.state}")

def transition_task_status(
    db: Session,
    task: ReminderTaskInstance,
    new_status: TaskStatus,
    completion_time: datetime = None,
) -> PastReminderEvent:
    """
    Transitions a ReminderTaskInstance status and creates an associated
    PastReminderEvent record in the clinical audit log.
    """
    # Ensure reminder and patient relationships are loaded
    if not task.reminder:
        task = (
            db.query(ReminderTaskInstance)
            .options(joinedload(ReminderTaskInstance.reminder))
            .filter(ReminderTaskInstance.id == task.id)
            .first()
        )

    reminder = task.reminder
    patient_id = reminder.patient_id if reminder else None
    med_name = reminder.medication_name if reminder else "Prescribed Medication"
    dosage = reminder.dosage if reminder else ""

    now_utc = datetime.now(timezone.utc)
    task.status = new_status

    if new_status == TaskStatus.COMPLETED:
        resolved = True
        actual_time = completion_time or now_utc
        task.completed_at = actual_time
        content = (
            f"Dose Completed: {med_name} {dosage} marked taken at "
            f"{actual_time.strftime('%Y-%m-%d %H:%M:%S UTC')} "
            f"(scheduled: {task.scheduled_time.strftime('%Y-%m-%d %H:%M:%S UTC')})."
        )
    elif new_status == TaskStatus.MISSED:
        resolved = False
        content = (
            f"Dose Missed: {med_name} {dosage} scheduled for "
            f"{task.scheduled_time.strftime('%Y-%m-%d %H:%M:%S UTC')} was not taken "
            f"within the 30-minute grace period."
        )
    else:
        resolved = False
        content = f"Task status updated to {new_status.value} for {med_name} {dosage}."

    event = PastReminderEvent(
        patient_id=patient_id,
        reminder_id=task.reminder_id,
        content=content,
        resolved_or_not=resolved,
        created_at=now_utc,
    )

    db.add(event)
    db.flush()
    return event





async def transition_monitor_task_status(
    db: Session,
    task: MonitorTaskInstance,
    new_status: TaskStatus,
    completion_time: Optional[datetime] = None,
    input_given: Optional[str] = None,
    user_notes: Optional[str] = None,
) -> PastMonitorEvent:
    """Transitions a MonitorTaskInstance status, evaluates telemetry via AI,

    provisions alerts when thresholds are breached, and commits a
    PastMonitorEvent audit record.
    """
    # 1. Ensure monitor and patient relationships are loaded
    if not task.monitor or not task.patient:
        task = (
            db.query(MonitorTaskInstance)
            .options(
                joinedload(MonitorTaskInstance.monitor),
                joinedload(MonitorTaskInstance.patient),
            )
            .filter(MonitorTaskInstance.id == task.id)
            .first()
        )

    now_utc = datetime.now(timezone.utc)
    task.status = new_status

    if input_given is not None:
        task.input_given = input_given
    if user_notes is not None:
        task.user_notes = user_notes

    if new_status == TaskStatus.COMPLETED:
        task.completed_at = completion_time or now_utc

    # 2. Extract clinical patient context
    patient = task.patient
    patient_summary = {
        "patient_id": task.patient_id,
        "name": getattr(patient, "name", "N/A"),
        "primary_diagnosis": getattr(patient, "primary_diagnosis", "N/A"),
        "hospital_course_description": getattr(
            patient, "hospital_course_description", "N/A"
        ),
    }

    # 3. Extract monitor specification
    monitor = task.monitor
    monitor_spec = {
        "instructions": monitor.instructions if monitor else "Telemetry check",
        "things_to_evaluate": monitor.things_to_evaluate if monitor else "N/A",
        "trigger_alert_if": monitor.trigger_alert_if if monitor else "N/A",
        "time": monitor.time if monitor else task.scheduled_time,
        "input_type": (
            monitor.input_type.value
            if (monitor and hasattr(monitor.input_type, "value"))
            else str(getattr(monitor, "input_type", "N/A"))
        ),
    }

    # 4. Fetch past remarks with timestamps from past_monitor_events table
    past_events = (
        db.query(PastMonitorEvent)
        .filter(
            PastMonitorEvent.patient_id == task.patient_id,
            PastMonitorEvent.monitor_id == task.monitor_id,
            PastMonitorEvent.remark.isnot(None),
        )
        .order_by(PastMonitorEvent.created_at.asc())
        .all()
    )

    past_remarks = [
        f"[{event.created_at.strftime('%Y-%m-%d %H:%M') if event.created_at else 'Unknown Date'}] {event.remark}"
        for event in past_events
        if event.remark and event.remark.strip()
    ]

    # 5. Consult AI triage evaluation
    if new_status == TaskStatus.COMPLETED:
        triage_result: MonitorTriageOutput = await evaluate_monitor_telemetry(
            patient_summary=patient_summary,
            monitor_spec=monitor_spec,
            past_remarks=past_remarks,
            media_path=task.input_given,
            user_notes=task.user_notes,
        )
    elif new_status == TaskStatus.MISSED:
        triage_result: MonitorTriageOutput = await evaluate_missed_telemetry(
            patient_summary=patient_summary,
            monitor_spec=monitor_spec,
            past_remarks=past_remarks,
        )
    else:
        triage_result = MonitorTriageOutput(
            alert_triggered=False,
            priority=AlertPriority.LOW,
            alert_content=None,
            evaluation_remark=f"Status updated to {new_status.value}.",
        )

    # 6. Create Alert if triggered
    if triage_result.alert_triggered:
        alert = Alert(
            patient_id=task.patient_id,
            monitor_id=task.monitor_id,
            priority=triage_result.priority,
            content=triage_result.alert_content
            or f"Alert triggered for monitor: {monitor_spec.get('instructions')}",
            monitor=task.monitor,
        )
        db.add(alert)

    # 7. Create PastMonitorEvent audit record
    final_input = task.input_given or (
        "No input provided (Missed)"
        if new_status == TaskStatus.MISSED
        else "Confirmed Completed"
    )

    event = PastMonitorEvent(
        patient_id=task.patient_id,
        monitor_id=task.monitor_id,
        input_given=final_input,
        remark=triage_result.evaluation_remark,
        alert_triggered_or_not=triage_result.alert_triggered,
        created_at=now_utc,
    )

    db.add(event)
    db.flush()
    return event