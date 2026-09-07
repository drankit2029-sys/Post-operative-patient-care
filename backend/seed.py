import sys
from datetime import date, datetime
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models import (
    Patient,
    Alert,
    Reminder,
    Monitor,
    PastReminderEvent,
    PastMonitorEvent,
    AlertPriority,
    ReminderFrequency,
    MonitorFrequency,
    InputType,
)

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Patient).count() > 0:
            print("Database already contains patient records. Skipping seed.")
            return

        # 1. Eleanor Vance
        p1 = Patient(
            patient_id="PT-904",
            name="Eleanor Vance",
            age=68,
            gender="Female",
            admission_date=date(2026, 8, 22),
            discharge_date=date(2026, 8, 30),
            primary_diagnosis="Acute Coronary Syndrome, Post-PCI with drug-eluting stent",
            hospital_course_description="Presented with retrosternal chest pressure. Deployed DES in mid-LAD.",
            treatment_summary=[{"treatment_name": "PCI", "duration": "1 day", "treatment_notes": "DES in mid-LAD."}],
            medications_at_discharge=[{"medication_name": "Aspirin", "dosage": "81 mg", "frequency": "Once daily", "duration": "Indefinite"}],
            discharge_instructions=[{"instruction": "Avoid heavy lifting >10 lbs."}],
            follow_up_appointments=[{"date": "2026-09-14", "department": "Cardiology", "provider": "Dr. Sarah Jenkins"}],
            responsible_physician={"name": "Dr. Sarah Jenkins", "contact": "+1 (555) 019-2834"},
            caretaker={"name": "Thomas Vance", "contact": "+1 (555) 234-5678", "relationship": "Spouse"},
            created_at=datetime(2026, 8, 30, 10, 15, 0)
        )
        db.add(p1)
        db.flush()

        rem1_1 = Reminder(patient_id=p1.patient_id, frequency=ReminderFrequency.DAILY, time="08:00", content="Take Aspirin 81mg and Ticagrelor 90mg with breakfast.", created_at=datetime(2026, 8, 30, 11, 0, 0))
        rem1_2 = Reminder(patient_id=p1.patient_id, frequency=ReminderFrequency.DAILY, time="20:00", content="Take Ticagrelor 90mg and Atorvastatin 80mg.", created_at=datetime(2026, 8, 30, 11, 0, 0))
        mon1 = Monitor(patient_id=p1.patient_id, frequency=MonitorFrequency.DAILY, input_type=InputType.IMAGE, time="10:00", instructions="Take photo of right groin puncture site.", things_to_evaluate="Check for hematoma or bleeding.", trigger_alert_if="Erythema exceeds 2cm or hematoma enlargement.", created_at=datetime(2026, 8, 30, 11, 30, 0))
        db.add_all([rem1_1, rem1_2, mon1])
        db.flush()

        # Alert tied to patient SpO2 (no specific monitor/reminder)
        db.add(Alert(patient_id=p1.patient_id, content="Critical drop in SpO2: 84% at resting state. Requires immediate assessment.", priority=AlertPriority.CRITICAL, created_at=datetime(2026, 9, 6, 18, 50, 0)))
        db.add(PastReminderEvent(patient_id=p1.patient_id, reminder_id=rem1_1.id, content="Morning antiplatelet dose confirmation.", resolved_or_not=True, created_at=datetime(2026, 9, 6, 8, 12, 0)))
        db.add(PastMonitorEvent(patient_id=p1.patient_id, monitor_id=mon1.id, input_given="/uploads/PT-904/groin_day6.jpg", remark="Puncture site clean.", alert_triggered_or_not=False, created_at=datetime(2026, 9, 5, 10, 14, 0)))

        # 2. Marcus Holloway
        p2 = Patient(
            patient_id="PT-882",
            name="Marcus Holloway",
            age=54,
            gender="Male",
            admission_date=date(2026, 8, 25),
            discharge_date=date(2026, 8, 28),
            primary_diagnosis="Hypertensive Emergency resolved",
            hospital_course_description="Admitted with acute headache and BP of 218/124 mmHg.",
            treatment_summary=[],
            medications_at_discharge=[],
            discharge_instructions=[],
            follow_up_appointments=[],
            responsible_physician={"name": "Dr. Ronald Patel", "contact": "+1 (555) 014-9821"},
            caretaker={"name": "Denise Holloway", "contact": "+1 (555) 876-5432", "relationship": "Sister"},
            created_at=datetime(2026, 8, 28, 14, 40, 0)
        )
        db.add(p2)
        db.flush()

        rem2 = Reminder(patient_id=p2.patient_id, frequency=ReminderFrequency.DAILY, time="19:30", content="Take Losartan 100mg.", created_at=datetime(2026, 8, 28, 15, 0, 0))
        mon2 = Monitor(patient_id=p2.patient_id, frequency=MonitorFrequency.DAILY, input_type=InputType.IMAGE, time="08:00", instructions="Capture photo of BP LCD screen.", things_to_evaluate="Evaluate BP.", trigger_alert_if="Systolic >= 170 mmHg.", created_at=datetime(2026, 8, 28, 15, 30, 0))
        db.add_all([rem2, mon2])
        db.flush()

        # Alert tied directly to Monitor #mon2
        db.add(Alert(patient_id=p2.patient_id, monitor_id=mon2.id, content="Acute systolic blood pressure spike detected: 178/95 mmHg.", priority=AlertPriority.CRITICAL, created_at=datetime(2026, 9, 6, 18, 42, 0)))
        db.add(PastMonitorEvent(patient_id=p2.patient_id, monitor_id=mon2.id, input_given="/uploads/PT-882/bp_reading_sept06.jpg", remark="Blood pressure readout shows 178/95 mmHg.", alert_triggered_or_not=True, created_at=datetime(2026, 9, 6, 18, 42, 0)))

        # 3. Sophia Reyes
        p3 = Patient(
            patient_id="PT-765",
            name="Sophia Reyes",
            age=42,
            gender="Female",
            admission_date=date(2026, 8, 21),
            discharge_date=date(2026, 8, 24),
            primary_diagnosis="Supraventricular Tachycardia",
            hospital_course_description="Catheter ablation for AVNRT.",
            treatment_summary=[],
            medications_at_discharge=[],
            discharge_instructions=[],
            follow_up_appointments=[],
            responsible_physician={"name": "Dr. Kevin Zhang", "contact": "+1 (555) 017-3312"},
            caretaker={"name": "Carlos Reyes", "contact": "+1 (555) 345-6789", "relationship": "Brother"},
            created_at=datetime(2026, 8, 24, 9, 0, 0)
        )
        db.add(p3)
        db.flush()

        rem3 = Reminder(patient_id=p3.patient_id, frequency=ReminderFrequency.DAILY, time="20:30", content="Take Metoprolol Tartrate 25mg.", created_at=datetime(2026, 8, 24, 10, 0, 0))
        db.add(rem3)
        db.flush()

        # Alert tied directly to Reminder #rem3
        db.add(Alert(patient_id=p3.patient_id, reminder_id=rem3.id, content="Missed scheduled evening medication: Metoprolol 25mg.", priority=AlertPriority.HIGH, created_at=datetime(2026, 9, 6, 18, 15, 0)))

        db.commit()
        print("Database re-seeded with reminder_id and monitor_id on alerts.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed()
