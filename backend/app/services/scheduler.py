import logging
from datetime import datetime, timedelta, date, time
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models import patient, alert, reminder, task_instance, monitor
from app.models.enums import TaskStatus, AlertPriority
from app.models.task_instance import ReminderTaskInstance,MonitorTaskInstance
from app.models.events import PastReminderEvent, PastMonitorEvent
from app.services.ai_evaluator import evaluate_missed_reminder, evaluate_monitor_telemetry, evaluate_missed_telemetry

Patient = patient.Patient
Alert = alert.Alert
Reminder = reminder.Reminder
ReminderTaskInstance = task_instance.ReminderTaskInstance
Monitor= monitor.Monitor
logger = logging.getLogger("scheduler")
scheduler = AsyncIOScheduler()

def parse_task_time(time_str: str) -> Optional[time]:
    try:
        parts = time_str.strip().split(":")
        return time(hour=int(parts[0]), minute=int(parts[1]))
    except Exception:
        return None

async def generate_daily_tasks():
    logger.info("Running daily task generation routine...")
    today = date.today()

    with SessionLocal() as db:
        reminders = db.scalars(
            select(Reminder)
        ).all()

        created_count = 0
        for rem in reminders:
            existing = db.scalar(
                select(ReminderTaskInstance).where(
                    and_(
                        ReminderTaskInstance.reminder_id == rem.id,
                        ReminderTaskInstance.scheduled_date == today,
                    )
                )
            )
            if not existing:
                new_task = ReminderTaskInstance(
                    reminder_id=rem.id,
                    patient_id=rem.patient_id,
                    scheduled_date=today,
                    scheduled_time=rem.time,
                    status=TaskStatus.PENDING,
                )
                db.add(new_task)
                created_count += 1

        db.commit()
        logger.info(f"Daily task generation completed: {created_count} tasks created.")

async def scan_overdue_tasks_and_triage():
    now = datetime.now()
    today = now.date()

    with SessionLocal() as db:
        pending_tasks = db.scalars(
            select(ReminderTaskInstance)
            .options(
                selectinload(ReminderTaskInstance.reminder),
                selectinload(ReminderTaskInstance.patient),
            )
            .where(
                and_(
                    ReminderTaskInstance.status == TaskStatus.PENDING,
                    ReminderTaskInstance.scheduled_date == today,
                )
            )
        ).all()

        for task in pending_tasks:
            t_obj = parse_task_time(task.scheduled_time)
            if not t_obj:
                continue

            scheduled_dt = datetime.combine(task.scheduled_date, t_obj)
            cutoff_dt = scheduled_dt + timedelta(minutes=30)

            if now >= cutoff_dt:
                logger.warning(
                    f"Task {task.id} for Patient {task.patient_id} lapsed >30m. Initiating AI triage..."
                )
                task.status = TaskStatus.MISSED

                med_info = task.reminder.content if task.reminder else "Scheduled Medication"

                # 1. Create the clinical audit log for the missed dose
                past_event = PastReminderEvent(
                    patient_id=task.patient_id,
                    reminder_id=task.reminder_id,
                    content=(
                        f"Dose Missed: '{med_info}' scheduled for {task.scheduled_time} "
                        f"on {task.scheduled_date} was not confirmed within the 30-minute grace period."
                    ),
                    resolved_or_not=False,
                    created_at=now,
                )
                db.add(past_event)

                # 2. Extract clinical context for AI triage
                patient = task.patient
                patient_summary = {
                    "patient_id": patient.patient_id,
                    "name": patient.name,
                    "age": patient.age,
                    "gender": patient.gender,
                    "primary_diagnosis": patient.primary_diagnosis,
                    "hospital_course_description": patient.hospital_course_description,
                    "medications_at_discharge": patient.medications_at_discharge or [],
                }

                # 3. AI triage and Alert generation
                try:
                    triage_result = await evaluate_missed_reminder(
                        patient_summary=patient_summary,
                        medication_info=med_info,
                        scheduled_time=task.scheduled_time,
                    )

                    new_alert = Alert(
                        patient_id=task.patient_id,
                        priority=triage_result.priority,
                        content=triage_result.alert_content + " " + triage_result.clinical_rationale,
                        reminder=task.reminder,
                    )
                    db.add(new_alert)
                    logger.info(
                        f"Alert created for {task.patient_id} [{triage_result.priority.value.upper()}]: "
                        f"{triage_result.alert_content}"
                    )
                except Exception as e:
                    logger.error(f"Failed to triage missed task {task.id}: {e}")

                db.commit()


def generate_daily_monitor_tasks():
    now = datetime.now()
    today = now.date()

    with SessionLocal() as db:
        active_monitors = db.scalars(
            select(Monitor)
        ).all()

        for monitor in active_monitors:
            existing = db.scalars(
                select(MonitorTaskInstance).where(
                    and_(
                        MonitorTaskInstance.monitor_id == monitor.id,
                        MonitorTaskInstance.scheduled_date == today,
                    )
                )
            ).first()

            if not existing:
                task = MonitorTaskInstance(
                    patient_id=monitor.patient_id,
                    monitor_id=monitor.id,
                    scheduled_date=today,
                    scheduled_time=monitor.time or "09:00",
                    status=TaskStatus.PENDING,
                )
                db.add(task)

        db.commit()

async def scan_overdue_monitors_and_triage():
    now = datetime.now()
    today = now.date()

    with SessionLocal() as db:
        # 1. Fetch all pending monitor tasks scheduled for today
        pending_tasks = db.scalars(
            select(MonitorTaskInstance)
            .options(
                selectinload(MonitorTaskInstance.monitor),
                selectinload(MonitorTaskInstance.patient),
            )
            .where(
                and_(
                    MonitorTaskInstance.status == TaskStatus.PENDING,
                    MonitorTaskInstance.scheduled_date == today,
                )
            )
        ).all()

        for task in pending_tasks:
            t_obj = parse_task_time(task.scheduled_time)
            if not t_obj:
                continue

            scheduled_dt = datetime.combine(task.scheduled_date, t_obj)
            cutoff_dt = scheduled_dt + timedelta(minutes=30)

            # Check if task is past the 30-minute grace window
            if now >= cutoff_dt:
                logger.warning(
                    f"Monitor Task {task.id} for Patient {task.patient_id} lapsed >30m. "
                    f"Initiating AI missed telemetry triage..."
                )
                task.status = TaskStatus.MISSED

                # 2. Extract clinical context from patient
                patient = task.patient
                patient_summary = {
                    "patient_id": patient.patient_id,
                    "name": patient.name,
                    "age": getattr(patient, "age", None),
                    "gender": getattr(patient, "gender", None),
                    "primary_diagnosis": patient.primary_diagnosis,
                    "hospital_course_description": patient.hospital_course_description,
                    "medications_at_discharge": getattr(patient, "medications_at_discharge", []) or [],
                }

                # 3. Build monitor protocol specification
                monitor = task.monitor
                monitor_spec = {
                    "instructions": monitor.instructions if monitor else "Scheduled telemetry check",
                    "things_to_evaluate": monitor.things_to_evaluate if monitor else "N/A",
                    "trigger_alert_if": monitor.trigger_alert_if if monitor else "N/A",
                    "time": monitor.time if monitor else task.scheduled_time,
                    "input_type": monitor.input_type.value if (monitor and hasattr(monitor.input_type, "value")) else str(getattr(monitor, "input_type", "N/A")),
                }

                # 4. Query past remarks with creation timestamp from PastMonitorEvent
                past_events = db.scalars(
                    select(PastMonitorEvent)
                    .where(
                        and_(
                            PastMonitorEvent.patient_id == task.patient_id,
                            PastMonitorEvent.monitor_id == task.monitor_id,
                            PastMonitorEvent.remark.is_not(None),
                        )
                    )
                    .order_by(PastMonitorEvent.created_at.asc())
                ).all()

                past_remarks = [
                    f"[{event.created_at.strftime('%Y-%m-%d %H:%M') if event.created_at else 'Unknown Date'}] {event.remark}"
                    for event in past_events
                    if event.remark and event.remark.strip()
                ]

                # Default fallback values in case triage encounters an unhandled exception
                alert_triggered = True
                alert_priority = AlertPriority.HIGH
                alert_content = f"Missed Telemetry: '{monitor_spec['instructions']}' scheduled for {task.scheduled_time} was not submitted."
                evaluation_remark = f"Patient missed scheduled telemetry submission (>30m overdue for {task.scheduled_time})."

                # 5. Invoke AI evaluation for missed telemetry
                try:
                    triage_result = await evaluate_missed_telemetry(
                        patient_summary=patient_summary,
                        monitor_spec=monitor_spec,
                        past_remarks=past_remarks,
                    )

                    alert_triggered = triage_result.alert_triggered
                    alert_priority = triage_result.priority
                    if triage_result.alert_content:
                        alert_content = triage_result.alert_content
                    if triage_result.evaluation_remark:
                        evaluation_remark = triage_result.evaluation_remark

                except Exception as e:
                    logger.error(f"Failed to triage missed monitor task {task.id}: {e}")

                # 6. Add an Alert if triggered
                if alert_triggered:
                    new_alert = Alert(
                        patient_id=task.patient_id,
                        monitor_id=task.monitor_id,
                        priority=alert_priority,
                        content=alert_content,
                        monitor=task.monitor,
                    )
                    db.add(new_alert)
                    logger.info(
                        f"Alert created for {task.patient_id} [{alert_priority.value.upper()}]: "
                        f"{alert_content}"
                    )

                # 7. Record the audit entry in PastMonitorEvent
                past_event = PastMonitorEvent(
                    patient_id=task.patient_id,
                    monitor_id=task.monitor_id,
                    input_given="No input provided (Missed)",
                    remark=evaluation_remark,
                    alert_triggered_or_not=alert_triggered,
                    created_at=now,
                )
                db.add(past_event)

                # Commit changes for this lapsed task
                db.commit()

def start_scheduler():
    if not scheduler.running:
        scheduler.add_job(
            scan_overdue_tasks_and_triage,
            "interval",
            minutes=1,
            id="scan_overdue_tasks",
            replace_existing=True,
        )
        scheduler.add_job(
            generate_daily_tasks,
            "cron",
            hour=2,
            minute=0,
            id="daily_task_generation",
            replace_existing=True,
        )
        scheduler.add_job(
            scan_overdue_monitors_and_triage,
            "interval",
            minutes=1,
            id="scan_overdue_monitors",
            replace_existing=True,
        )
        scheduler.add_job(
            generate_daily_monitor_tasks,
            "cron",
            hour=2,
            minute=0,
            id="daily_monitor_task_generation",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("APScheduler initialized and running.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
