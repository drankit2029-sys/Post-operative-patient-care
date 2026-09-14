from datetime import date, datetime, timedelta, timezone
from app.db.session import SessionLocal
from app.models.enums import (
    AlertPriority,
    InputType,
    MonitorFrequency,
    ReminderFrequency,
    TaskStatus,
)
from app.models.patient import Patient
from app.models.reminder import Reminder
from app.models.monitor import Monitor
from app.models.task_instance import ReminderTaskInstance
from app.models.task_instance import MonitorTaskInstance
from app.models.events import PastReminderEvent, PastMonitorEvent
from app.models.alert import Alert


def seed_pt820():
    with SessionLocal() as db:
        patient_id = "PT-820"
        today = date.today()
        now_utc = datetime.now(timezone.utc)

        # 1. Fetch or create Patient PT-820
        patient = db.query(Patient).filter_by(patient_id=patient_id).first()
        if not patient:
            patient = Patient(
                patient_id=patient_id,
                name="Vikramaditya Rao",
                age=54,
                gender="Male",
                admission_date=today - timedelta(days=7),
                discharge_date=today - timedelta(days=2),
                primary_diagnosis="Laparoscopic Cholecystectomy, Day 5 Post-Op",
                hospital_course_description=(
                    "Underwent elective laparoscopic cholecystectomy for symptomatic cholelithiasis. "
                    "Procedure uneventful with minimal blood loss. Discharged on standard antibiotics, "
                    "analgesics, and wound telemetry monitoring."
                ),
                treatment_summary=[
                    {"procedure": "Laparoscopic Cholecystectomy", "date": str(today - timedelta(days=6))}
                ],
                medications_at_discharge=[
                    {"drug": "Cefuroxime", "dose": "500mg", "route": "PO", "frequency": "BID"},
                    {"drug": "Pantoprazole", "dose": "40mg", "route": "PO", "frequency": "OD"},
                    {"drug": "Ultracet", "dose": "1 tab", "route": "PO", "frequency": "PRN"},
                ],
                discharge_instructions=[
                    {"instruction": "Keep umbilical and subcostal port sites dry and clean."},
                    {"instruction": "Avoid strenuous lifting (> 5 kg) for 3 weeks."},
                    {"instruction": "Report acute right upper quadrant pain or fever immediately."},
                ],
                follow_up_appointments=[
                    {"clinic": "Surgical OPD", "date": str(today + timedelta(days=7)), "time": "10:30 AM"}
                ],
                responsible_physician={
                    "name": "Dr. R. S. Iyer",
                    "specialty": "Minimally Invasive Surgery",
                    "contact": "+91-9876541230",
                },
                additional_notes=[
                    {"note": "Tolerating soft diet well. Port-site dressing intact."}
                ],
                caretaker={
                    "name": "Meera Rao",
                    "relationship": "Spouse",
                    "phone": "+91-9876543219",
                },
            )
            db.add(patient)
            db.flush()

        # 2. Clean previous child data for idempotent seeding
        db.query(Alert).filter_by(patient_id=patient_id).delete()
        db.query(PastReminderEvent).filter_by(patient_id=patient_id).delete()
        db.query(PastMonitorEvent).filter_by(patient_id=patient_id).delete()
        db.query(ReminderTaskInstance).filter_by(patient_id=patient_id).delete()
        db.query(MonitorTaskInstance).filter_by(patient_id=patient_id).delete()
        db.query(Reminder).filter_by(patient_id=patient_id).delete()
        db.query(Monitor).filter_by(patient_id=patient_id).delete()
        db.flush()

        # 3. Create Reminders
        rem_morning = Reminder(
            patient_id=patient_id,
            frequency=ReminderFrequency.DAILY,
            time="08:00",
            content="Cefuroxime 500mg tablet - Oral after breakfast",
        )
        rem_evening = Reminder(
            patient_id=patient_id,
            frequency=ReminderFrequency.DAILY,
            time="20:00",
            content="Cefuroxime 500mg tablet - Oral after dinner",
        )
        rem_prn = Reminder(
            patient_id=patient_id,
            frequency=ReminderFrequency.DAILY,
            time="14:00",
            content="Ultracet (Tramadol/APAP) 1 tablet - Post-op pain management",
        )
        db.add_all([rem_morning, rem_evening, rem_prn])
        db.flush()

        # 4. Create Monitors
        mon_wound = Monitor(
            patient_id=patient_id,
            frequency=MonitorFrequency.DAILY,
            input_type=InputType.IMAGE,
            time="09:00",
            instructions="Submit well-lit photograph of umbilical and subcostal trocar incisions.",
            things_to_evaluate="Erythema, serosanguinous or purulent discharge, wound gaping.",
            trigger_alert_if="Discharge oozing from port site or expanding redness > 1.5 cm.",
        )
        mon_vitals = Monitor(
            patient_id=patient_id,
            frequency=MonitorFrequency.DAILY,
            input_type=InputType.VIDEO,
            time="17:00",
            instructions="Record 15-second video walking unassisted to evaluate abdominal splinting.",
            things_to_evaluate="Guarding, severe pain grimace, unsteady gait.",
            trigger_alert_if="Severe antalgic gait or guarding indicating acute peritonitis.",
        )
        db.add_all([mon_wound, mon_vitals])
        db.flush()

        # 5. Create ReminderTaskInstances
        # Morning dose: Completed
        task_rem_completed = ReminderTaskInstance(
            reminder_id=rem_morning.id,
            patient_id=patient_id,
            scheduled_date=today,
            scheduled_time="08:00",
            status=TaskStatus.COMPLETED,
            completed_at=datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=8, minutes=7),
        )
        # Afternoon dose: Missed (lapsed past grace period)
        task_rem_missed = ReminderTaskInstance(
            reminder_id=rem_prn.id,
            patient_id=patient_id,
            scheduled_date=today,
            scheduled_time="14:00",
            status=TaskStatus.MISSED,
            completed_at=None,
        )
        # Evening dose: Pending
        task_rem_pending = ReminderTaskInstance(
            reminder_id=rem_evening.id,
            patient_id=patient_id,
            scheduled_date=today,
            scheduled_time="20:00",
            status=TaskStatus.PENDING,
            completed_at=None,
        )
        db.add_all([task_rem_completed, task_rem_missed, task_rem_pending])

        # 6. Create MonitorTaskInstances
        # Morning wound check: Completed with upload
        task_mon_completed = MonitorTaskInstance(
            monitor_id=mon_wound.id,
            patient_id=patient_id,
            scheduled_date=today,
            scheduled_time="09:00",
            status=TaskStatus.COMPLETED,
            completed_at=datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc) + timedelta(hours=9, minutes=14),
            input_given="uploads/patients/PT-820/monitors/port_site_day5.jpg",
            user_notes="Incision sites dry, minimal tenderness around the navel.",
        )
        # Evening video check: Pending
        task_mon_pending = MonitorTaskInstance(
            monitor_id=mon_vitals.id,
            patient_id=patient_id,
            scheduled_date=today,
            scheduled_time="17:00",
            status=TaskStatus.PENDING,
            completed_at=None,
            input_given=None,
            user_notes=None,
        )
        # Yesterday's wound check: Missed
        task_mon_missed = MonitorTaskInstance(
            monitor_id=mon_wound.id,
            patient_id=patient_id,
            scheduled_date=today - timedelta(days=1),
            scheduled_time="09:00",
            status=TaskStatus.MISSED,
            completed_at=None,
            input_given=None,
            user_notes="Patient reported poor internet connectivity.",
        )
        db.add_all([task_mon_completed, task_mon_pending, task_mon_missed])

        # 7. Create PastReminderEvents
        past_rem_completed = PastReminderEvent(
            patient_id=patient_id,
            reminder_id=rem_morning.id,
            content="Dose Completed: Cefuroxime 500mg confirmed taken at 08:07 UTC.",
            resolved_or_not=True,
            created_at=now_utc - timedelta(hours=4),
        )
        past_rem_missed = PastReminderEvent(
            patient_id=patient_id,
            reminder_id=rem_prn.id,
            content="Dose Missed: Ultracet 1 tab scheduled for 14:00 lapsed past 30-minute grace window.",
            resolved_or_not=False,
            created_at=now_utc - timedelta(hours=1),
        )
        db.add_all([past_rem_completed, past_rem_missed])

        # 8. Create PastMonitorEvents
        past_mon_good = PastMonitorEvent(
            patient_id=patient_id,
            monitor_id=mon_wound.id,
            input_given="uploads/patients/PT-820/monitors/port_site_day5.jpg",
            remark="Port site dressings clean and intact. No peri-incisional erythema or drainage observed.",
            alert_triggered_or_not=False,
            created_at=now_utc - timedelta(hours=3),
        )
        past_mon_missed = PastMonitorEvent(
            patient_id=patient_id,
            monitor_id=mon_wound.id,
            input_given="No input provided (Missed)",
            remark="Mandatory morning surgical wound telemetry not received within grace window.",
            alert_triggered_or_not=True,
            created_at=now_utc - timedelta(days=1, hours=6),
        )
        db.add_all([past_mon_good, past_mon_missed])
        db.flush()

        # 9. Create Alerts
        alert_medication = Alert(
            patient_id=patient_id,
            reminder_id=rem_prn.id,
            monitor_id=None,
            content="MISSED DOSE ALERT: Analgesic Ultracet lapsed >30m. Monitor for acute breakthrough pain.",
            priority=AlertPriority.MEDIUM,
            created_at=now_utc - timedelta(hours=1),
        )
        alert_monitor = Alert(
            patient_id=patient_id,
            reminder_id=None,
            monitor_id=mon_wound.id,
            content="OVERDUE MONITOR: Surgical port-site image check pending for >24 hours.",
            priority=AlertPriority.HIGH,
            created_at=now_utc - timedelta(days=1, hours=6),
        )
        db.add_all([alert_medication, alert_monitor])

        db.commit()


if __name__ == "__main__":
    seed_pt820()
    print("Database seeded with sample workflow for patient PT-820.")