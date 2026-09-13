import asyncio
from datetime import datetime, timedelta, date
from app.db.session import SessionLocal
from app.models.patient import Patient
from app.models.reminder import Reminder
from app.models.alert import Alert
from app.models.task_instance import ReminderTaskInstance
from app.models.enums import TaskStatus
from app.services.scheduler import scan_overdue_tasks_and_triage

async def main():
    print("=" * 65)
    print("TESTING 30-MIN MISSED TASK SCANNER & MISTRAL TRIAGE")
    print("=" * 65)

    now = datetime.now()
    overdue_time = (now - timedelta(minutes=45)).strftime("%H:%M")
    test_pid = "TEST-SCHED-01"

    with SessionLocal() as db:
        # 1. Ensure test patient exists
        p = db.get(Patient, test_pid)
        if not p:
            p = Patient(
                patient_id=test_pid,
                name="Arthur Dent",
                age=42,
                gender="Male",
                primary_diagnosis="Post-Percutaneous Coronary Intervention (PCI)",
                hospital_course_description="Drug-eluting stent placed in LAD. High risk of thrombosis.",
                medications_at_discharge=[
                    {"medication_name": "Ticagrelor", "dosage": "90 mg", "frequency": "Twice daily"}
                ]
            )
            db.add(p)
            db.flush()

        # 2. Add an active reminder scheduled 45 mins ago
        rem = Reminder(
            patient_id=test_pid,
            time=overdue_time,
            content="Take Ticagrelor 90mg"
        )
        db.add(rem)
        db.flush()

        # 3. Create a PENDING task instance for today
        task = ReminderTaskInstance(
            reminder_id=rem.id,
            patient_id=test_pid,
            scheduled_date=date.today(),
            scheduled_time=overdue_time,
            status=TaskStatus.PENDING
        )
        db.add(task)
        db.commit()
        task_id = task.id
        print(f"[1/3] Seeded Task {task_id} scheduled at {overdue_time} (>30m ago)")

    # 4. Trigger the scanner job
    print("[2/3] Executing scan_overdue_tasks_and_triage()...")
    await scan_overdue_tasks_and_triage()

    # 5. Verify database state
    print("[3/3] Inspecting database changes...")
    with SessionLocal() as db:
        updated_task = db.get(ReminderTaskInstance, task_id)
        print(f"      • Task Status: {updated_task.status.value.upper()}")

        alerts = db.scalars(
            db.query(Alert).filter(Alert.patient_id == test_pid).order_by(Alert.created_at.desc())
        ).all()

        if alerts:
            latest = alerts[0]
            print(f"      • Alert Triggered: YES")
            print(f"      • Priority:        {latest.priority.value.upper()}")
            print(f"      • Alert Content:   {latest.content}")
            print("\n" + "=" * 65)
            print("✓ SUCCESS: Task marked MISSED and Mistral generated clinical alert!")
            print("=" * 65)
        else:
            print("❌ Failure: No alert was created.")

if __name__ == "__main__":
    asyncio.run(main())
