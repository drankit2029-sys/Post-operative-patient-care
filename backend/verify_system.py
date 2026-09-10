import sys
from datetime import date, datetime
from sqlalchemy import inspect, select

def run_checks():
    print("=" * 50)
    print("RUNNING POST-IMPLEMENTATION VERIFICATION")
    print("=" * 50)

    # 1. Check Model Imports & Circular Dependencies
    print("\n[1/5] Checking Model Imports...")
    try:
        from app.models import (
            Patient,
            Alert,
            Reminder,
            Monitor,
            PastReminderEvent,
            PastMonitorEvent,
            ReminderTaskInstance,
            TaskStatus,
            AlertPriority,
            ReminderFrequency,
            MonitorFrequency,
            InputType
        )
        print("  ✓ All models and enums imported cleanly.")
    except Exception as e:
        print(f"  ✗ Model import failed: {e}")
        sys.exit(1)

    # 2. Check Database Tables in SQLite
    print("\n[2/5] Checking SQLite Table Schema...")
    from app.db.session import engine, SessionLocal
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = [
        "patients",
        "alerts",
        "reminders",
        "monitors",
        "past_reminder_events",
        "past_monitor_events",
        "reminder_task_instances"
    ]
    missing = [t for t in expected_tables if t not in tables]
    if missing:
        print(f"  ✗ Missing tables in database: {missing}")
        sys.exit(1)
    print(f"  ✓ All {len(expected_tables)} tables present: {', '.join(tables)}")

    # 3. Check Relationships and CRUD on ReminderTaskInstance
    print("\n[3/5] Checking Database Relationships & Task Instances...")
    db = SessionLocal()
    try:
        patient = db.scalar(select(Patient).limit(1))
        if not patient:
            print("  ✗ No patients found in DB. Run 'python seed.py' first.")
            sys.exit(1)

        reminder = db.scalar(select(Reminder).where(Reminder.patient_id == patient.patient_id).limit(1))
        if not reminder:
            print(f"  ✗ No reminders found for patient {patient.patient_id}.")
            sys.exit(1)

        # Create a test instance
        test_instance = ReminderTaskInstance(
            reminder_id=reminder.id,
            patient_id=patient.patient_id,
            scheduled_date=date.today(),
            scheduled_time=reminder.time,
            status=TaskStatus.PENDING
        )
        db.add(test_instance)
        db.commit()
        db.refresh(test_instance)

        # Verify Bidirectional Relationships
        db.refresh(patient)
        db.refresh(reminder)
        assert test_instance in patient.reminder_task_instances, "Relationship patient.reminder_task_instances failed"
        assert test_instance in reminder.task_instances, "Relationship reminder.task_instances failed"
        assert test_instance.patient.patient_id == patient.patient_id, "Reverse patient link failed"
        assert test_instance.reminder.id == reminder.id, "Reverse reminder link failed"

        print(f"  ✓ Created and verified TaskInstance #{test_instance.id} (Status: {test_instance.status.value}).")
        print("  ✓ Bidirectional SQLAlchemy relationships operational.")

        # Cleanup test entry
        db.delete(test_instance)
        db.commit()
        print("  ✓ Cleanup completed successfully.")
    except Exception as e:
        db.rollback()
        print(f"  ✗ Database relationship test failed: {e}")
        sys.exit(1)
    finally:
        db.close()

    # 4. Check Pydantic Schemas Serialization
    print("\n[4/5] Checking Pydantic v2 Schemas...")
    try:
        from app.schemas.task_instance import (
            ReminderTaskInstanceCreate,
            ReminderTaskInstanceResponse
        )
        test_payload = ReminderTaskInstanceCreate(
            reminder_id=1,
            patient_id="PT-904",
            scheduled_date=date.today(),
            scheduled_time="08:00",
            status=TaskStatus.PENDING
        )
        serialized = test_payload.model_dump()
        assert serialized["status"] == "pending", "Enum serialization failed"
        print("  ✓ TaskInstance Pydantic schemas serialize and validate accurately.")
    except Exception as e:
        print(f"  ✗ Schema validation failed: {e}")
        sys.exit(1)

    # 5. Check FastAPI App & Route Mounting
    print("\n[5/5] Checking FastAPI Router & Route Health...")
    try:
        from app.main import app
        route_paths = [r.path for r in app.routes]
        essential_routes = [
            "/api/v1/health",
            "/api/v1/patients/count",
            "/api/v1/alerts",
            "/api/v1/patients",
            "/api/v1/patients/{patient_id}",
            "/api/v1/patients/{patient_id}/reminders",
            "/api/v1/patients/{patient_id}/monitors"
        ]
        for route in essential_routes:
            assert route in route_paths, f"Missing route: {route}"
        print(f"  ✓ FastAPI ASGI app loaded. All {len(essential_routes)} core routes mounted.")
    except Exception as e:
        print(f"  ✗ FastAPI app failed to initialize: {e}")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("ALL CHECKS PASSED: SYSTEM INTEGRITY VERIFIED")
    print("=" * 50)

if __name__ == "__main__":
    run_checks()
