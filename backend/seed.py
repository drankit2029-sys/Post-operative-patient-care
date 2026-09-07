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
            hospital_course_description="Presented with retrosternal chest pressure and troponin elevation. Deployed DES in mid-LAD.",
            treatment_summary=[{"treatment_name": "PCI", "duration": "1 day", "treatment_notes": "DES placed in mid-LAD."}],
            medications_at_discharge=[{"medication_name": "Aspirin", "dosage": "81 mg", "frequency": "Once daily", "duration": "Indefinite"}],
            discharge_instructions=[{"instruction": "Avoid heavy lifting greater than 10 lbs for 2 weeks."}],
            follow_up_appointments=[{"date": "2026-09-14", "department": "Cardiology", "provider": "Dr. Sarah Jenkins"}],
            responsible_physician={"name": "Dr. Sarah Jenkins", "contact": "+1 (555) 019-2834"},
            additional_notes=[{"note": "Patient exhibits baseline mild anxiety."}],
            caretaker={"name": "Thomas Vance", "contact": "+1 (555) 234-5678", "relationship": "Spouse"},
            created_at=datetime(2026, 8, 30, 10, 15, 0)
        )
        db.add(p1)
        db.flush()

        db.add(Alert(patient_id=p1.patient_id, content="Critical drop in SpO2: 84% at resting state. Requires immediate assessment.", priority=AlertPriority.CRITICAL, created_at=datetime(2026, 9, 6, 18, 50, 0)))
        rem1_1 = Reminder(patient_id=p1.patient_id, frequency=ReminderFrequency.DAILY, time="08:00", content="Take Aspirin 81mg and Ticagrelor 90mg with breakfast.", created_at=datetime(2026, 8, 30, 11, 0, 0))
        rem1_2 = Reminder(patient_id=p1.patient_id, frequency=ReminderFrequency.DAILY, time="20:00", content="Take Ticagrelor 90mg and Atorvastatin 80mg.", created_at=datetime(2026, 8, 30, 11, 0, 0))
        mon1 = Monitor(patient_id=p1.patient_id, frequency=MonitorFrequency.DAILY, input_type=InputType.IMAGE, time="10:00", instructions="Take photo of right groin puncture site.", things_to_evaluate="Check for hematoma or bleeding.", trigger_alert_if="Erythema exceeds 2cm or hematoma enlargement.", created_at=datetime(2026, 8, 30, 11, 30, 0))
        db.add_all([rem1_1, rem1_2, mon1])
        db.flush()

        db.add(PastReminderEvent(patient_id=p1.patient_id, reminder_id=rem1_1.id, content="Morning antiplatelet dose confirmation.", resolved_or_not=True, created_at=datetime(2026, 9, 6, 8, 12, 0)))
        db.add(PastMonitorEvent(patient_id=p1.patient_id, monitor_id=mon1.id, input_given="/uploads/PT-904/groin_day6.jpg", remark="Puncture site clean, minimal bruising.", alert_triggered_or_not=False, created_at=datetime(2026, 9, 5, 10, 14, 0)))

        # 2. Marcus Holloway
        p2 = Patient(
            patient_id="PT-882",
            name="Marcus Holloway",
            age=54,
            gender="Male",
            admission_date=date(2026, 8, 25),
            discharge_date=date(2026, 8, 28),
            primary_diagnosis="Hypertensive Emergency resolved, Essential Hypertension Stage II",
            hospital_course_description="Admitted with acute headache and BP of 218/124 mmHg. Controlled with IV Nicardipine.",
            treatment_summary=[{"treatment_name": "IV Nicardipine", "duration": "24 hours", "treatment_notes": "Gradual MAP decrease."}],
            medications_at_discharge=[{"medication_name": "Amlodipine", "dosage": "10 mg", "frequency": "Once daily", "duration": "Ongoing"}],
            discharge_instructions=[{"instruction": "Maintain strict low-sodium dietary restriction."}],
            follow_up_appointments=[{"date": "2026-09-08", "department": "Internal Medicine", "provider": "Dr. Ronald Patel"}],
            responsible_physician={"name": "Dr. Ronald Patel", "contact": "+1 (555) 014-9821"},
            additional_notes=[{"note": "Patient had self-discontinued meds 3 months prior."}],
            caretaker={"name": "Denise Holloway", "contact": "+1 (555) 876-5432", "relationship": "Sister"},
            created_at=datetime(2026, 8, 28, 14, 40, 0)
        )
        db.add(p2)
        db.flush()

        db.add(Alert(patient_id=p2.patient_id, content="Acute systolic blood pressure spike detected: 178/95 mmHg.", priority=AlertPriority.CRITICAL, created_at=datetime(2026, 9, 6, 18, 42, 0)))
        rem2_1 = Reminder(patient_id=p2.patient_id, frequency=ReminderFrequency.DAILY, time="07:30", content="Take Amlodipine 10mg and Chlorthalidone 25mg.", created_at=datetime(2026, 8, 28, 15, 0, 0))
        rem2_2 = Reminder(patient_id=p2.patient_id, frequency=ReminderFrequency.DAILY, time="19:30", content="Take Losartan 100mg.", created_at=datetime(2026, 8, 28, 15, 0, 0))
        mon2 = Monitor(patient_id=p2.patient_id, frequency=MonitorFrequency.DAILY, input_type=InputType.IMAGE, time="08:00", instructions="Capture photo of BP LCD screen.", things_to_evaluate="Evaluate systolic/diastolic values.", trigger_alert_if="Systolic >= 170 mmHg.", created_at=datetime(2026, 8, 28, 15, 30, 0))
        db.add_all([rem2_1, rem2_2, mon2])
        db.flush()

        db.add(PastReminderEvent(patient_id=p2.patient_id, reminder_id=rem2_2.id, content="Evening Losartan dose confirmation.", resolved_or_not=True, created_at=datetime(2026, 9, 5, 19, 45, 0)))
        db.add(PastMonitorEvent(patient_id=p2.patient_id, monitor_id=mon2.id, input_given="/uploads/PT-882/bp_reading_sept06.jpg", remark="Readout shows 178/95 mmHg.", alert_triggered_or_not=True, created_at=datetime(2026, 9, 6, 18, 42, 0)))

        # 3. Sophia Reyes
        p3 = Patient(
            patient_id="PT-765",
            name="Sophia Reyes",
            age=42,
            gender="Female",
            admission_date=date(2026, 8, 21),
            discharge_date=date(2026, 8, 24),
            primary_diagnosis="Supraventricular Tachycardia (Ablated), Hypokalemia",
            hospital_course_description="Elective EP study and RF catheter ablation for AVNRT.",
            treatment_summary=[{"treatment_name": "RF Ablation", "duration": "1 day", "treatment_notes": "Successful slow pathway ablation."}],
            medications_at_discharge=[{"medication_name": "Metoprolol Tartrate", "dosage": "25 mg", "frequency": "Twice daily", "duration": "4 weeks"}],
            discharge_instructions=[{"instruction": "Refrain from strenuous workouts for 10 days."}],
            follow_up_appointments=[{"date": "2026-09-22", "department": "EP Clinic", "provider": "Dr. Kevin Zhang"}],
            responsible_physician={"name": "Dr. Kevin Zhang", "contact": "+1 (555) 017-3312"},
            additional_notes=[],
            caretaker={"name": "Carlos Reyes", "contact": "+1 (555) 345-6789", "relationship": "Brother"},
            created_at=datetime(2026, 8, 24, 9, 0, 0)
        )
        db.add(p3)
        db.flush()

        db.add(Alert(patient_id=p3.patient_id, content="Missed scheduled evening medication: Metoprolol 25mg.", priority=AlertPriority.HIGH, created_at=datetime(2026, 9, 6, 18, 15, 0)))
        rem3 = Reminder(patient_id=p3.patient_id, frequency=ReminderFrequency.DAILY, time="08:30", content="Take Metoprolol Tartrate 25mg.", created_at=datetime(2026, 8, 24, 10, 0, 0))
        mon3 = Monitor(patient_id=p3.patient_id, frequency=MonitorFrequency.DAILY, input_type=InputType.VIDEO, time="09:00", instructions="Record pulse video.", things_to_evaluate="Rhythm regularity.", trigger_alert_if="HR > 110 bpm.", created_at=datetime(2026, 8, 24, 10, 30, 0))
        db.add_all([rem3, mon3])
        db.flush()

        db.add(PastReminderEvent(patient_id=p3.patient_id, reminder_id=rem3.id, content="Morning beta blocker dose.", resolved_or_not=True, created_at=datetime(2026, 9, 6, 8, 35, 0)))

        # 4. Arthur Pendelton
        p4 = Patient(
            patient_id="PT-630",
            name="Arthur Pendelton",
            age=73,
            gender="Male",
            admission_date=date(2026, 8, 14),
            discharge_date=date(2026, 8, 20),
            primary_diagnosis="Type 2 Diabetes Mellitus with hyperosmolar state, Diabetic Nephropathy",
            hospital_course_description="Presented with altered sensorium and glucose 740 mg/dL. Rehydrated with IV fluids and insulin protocol.",
            treatment_summary=[{"treatment_name": "IV Fluids & Insulin", "duration": "3 days", "treatment_notes": "Mentation returned to baseline."}],
            medications_at_discharge=[{"medication_name": "Insulin Glargine", "dosage": "24 units", "frequency": "Once daily", "duration": "Ongoing"}],
            discharge_instructions=[{"instruction": "Check glucose before every meal."}],
            follow_up_appointments=[{"date": "2026-09-10", "department": "Endocrinology", "provider": "Dr. Anita Desai"}],
            responsible_physician={"name": "Dr. Anita Desai", "contact": "+1 (555) 012-7788"},
            additional_notes=[],
            caretaker={"name": "Margaret Pendelton", "contact": "+1 (555) 987-6543", "relationship": "Daughter"},
            created_at=datetime(2026, 8, 20, 11, 20, 0)
        )
        db.add(p4)
        db.flush()

        db.add(Alert(patient_id=p4.patient_id, content="Continuous glucose monitor indicates persistent hypoglycemia (<60 mg/dL).", priority=AlertPriority.CRITICAL, created_at=datetime(2026, 9, 6, 17, 30, 0)))
        rem4 = Reminder(patient_id=p4.patient_id, frequency=ReminderFrequency.DAILY, time="21:00", content="Administer 24 units Insulin Glargine subcutaneously.", created_at=datetime(2026, 8, 20, 12, 0, 0))
        mon4 = Monitor(patient_id=p4.patient_id, frequency=MonitorFrequency.DAILY, input_type=InputType.IMAGE, time="20:00", instructions="Take photos of soles of both feet.", things_to_evaluate="Check for ulcerations.", trigger_alert_if="New redness or drainage.", created_at=datetime(2026, 8, 20, 12, 30, 0))
        db.add_all([rem4, mon4])
        db.flush()

        db.add(PastReminderEvent(patient_id=p4.patient_id, reminder_id=rem4.id, content="Bedtime basal insulin injection confirmation.", resolved_or_not=True, created_at=datetime(2026, 9, 5, 21, 10, 0)))
        db.add(PastMonitorEvent(patient_id=p4.patient_id, monitor_id=mon4.id, input_given="/uploads/PT-630/feet_check_sept05.jpg", remark="Plantar skin intact.", alert_triggered_or_not=False, created_at=datetime(2026, 9, 5, 20, 15, 0)))

        # 5. Amara Chen
        p5 = Patient(
            patient_id="PT-512",
            name="Amara Chen",
            age=36,
            gender="Female",
            admission_date=date(2026, 8, 9),
            discharge_date=date(2026, 8, 15),
            primary_diagnosis="Community-Acquired Pneumonia (Resolved), Asthma Exacerbation",
            hospital_course_description="Presented with fever and wheezing. Responded well to IV Ceftriaxone and methylprednisolone.",
            treatment_summary=[{"treatment_name": "Antibiotic & Steroid Therapy", "duration": "4 days", "treatment_notes": "Oral switch on day 5."}],
            medications_at_discharge=[{"medication_name": "Advair Diskus 250/50", "dosage": "1 inhalation", "frequency": "Twice daily", "duration": "Ongoing"}],
            discharge_instructions=[{"instruction": "Rinse mouth after Advair."}],
            follow_up_appointments=[{"date": "2026-09-12", "department": "Pulmonology", "provider": "Dr. Elena Rostova"}],
            responsible_physician={"name": "Dr. Elena Rostova", "contact": "+1 (555) 015-4429"},
            additional_notes=[],
            caretaker={"name": "David Chen", "contact": "+1 (555) 432-1098", "relationship": "Spouse"},
            created_at=datetime(2026, 8, 15, 8, 30, 0)
        )
        db.add(p5)
        db.flush()

        rem5 = Reminder(patient_id=p5.patient_id, frequency=ReminderFrequency.DAILY, time="08:00", content="Inhale Advair 250/50.", created_at=datetime(2026, 8, 15, 9, 0, 0))
        mon5 = Monitor(patient_id=p5.patient_id, frequency=MonitorFrequency.DAILY, input_type=InputType.IMAGE, time="08:15", instructions="Take photo of peak flow meter.", things_to_evaluate="Evaluate PEFR.", trigger_alert_if="Peak flow falls below 320 L/min.", created_at=datetime(2026, 8, 15, 9, 30, 0))
        db.add_all([rem5, mon5])
        db.flush()

        db.add(PastReminderEvent(patient_id=p5.patient_id, reminder_id=rem5.id, content="Morning inhaler maintenance dose.", resolved_or_not=True, created_at=datetime(2026, 9, 6, 8, 5, 0)))
        db.add(PastMonitorEvent(patient_id=p5.patient_id, monitor_id=mon5.id, input_given="/uploads/PT-512/pefr_sept06.jpg", remark="Peak flow meter shows 390 L/min.", alert_triggered_or_not=False, created_at=datetime(2026, 9, 6, 8, 20, 0)))

        db.commit()
        print("Database re-seeded successfully with foreign key links between past events, reminders, and monitors.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed()
