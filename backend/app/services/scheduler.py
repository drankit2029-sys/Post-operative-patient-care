import logging
from datetime import datetime, timedelta, date, time
from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models import patient, alert, reminder, task_instance 
from app.models.enums import TaskStatus, AlertPriority
from app.services.ai_evaluator import evaluate_missed_reminder

Patient = patient.Patient
Alert = alert.Alert
reminder = reminder.Reminder
ReminderTaskInstance = task_instance.ReminderTaskInstance
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
            select(Reminder).where(Reminder.is_active == True)
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

                med_info = task.reminder.content if task.reminder else "Scheduled Medication"

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
                        reminder=task.reminder)
                    db.add(new_alert)
                    logger.info(
                        f"Alert created for {task.patient_id} [{triage_result.priority.value.upper()}]: "
                        f"{triage_result.alert_content}"
                    )
                except Exception as e:
                    logger.error(f"Failed to triage missed task {task.id}: {e}")

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
            hour=0,
            minute=1,
            id="daily_task_generation",
            replace_existing=True,
        )
        scheduler.start()
        logger.info("APScheduler initialized and running.")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("APScheduler stopped.")
