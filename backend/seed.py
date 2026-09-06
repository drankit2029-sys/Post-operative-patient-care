import sys
from datetime import date, datetime, timedelta
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
    # Ensure database schema is created
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if records already exist
        if db.query(Patient).count() > 0:
            print("Database already contains patient records. Skipping seed.")
            return

        patients_data = [
            {
                "patient": Patient(
                    patient_id="PT-904",
                    name="Eleanor Vance",
                    age=68,
                    gender="Female",
                    admission_date=date(2026, 8, 22),
                    discharge_date=date(2026, 8, 30),
                    primary_diagnosis="Acute Coronary Syndrome, Post-PCI with drug-eluting stent",
                    hospital_course_description="Presented with retrosternal chest pressure and troponin elevation. Emergent coronary angiography revealed 90% occlusion in the mid-LAD. Successful drug-eluting stent deployed. Post-procedure telemetry remained stable without recurrent arrhythmias.",
                    treatment_summary=[
                        {
                            "treatment_name": "Percutaneous Coronary Intervention (PCI)",
                            "duration": "1 day",
                            "treatment_notes": "Single DES placed in mid-LAD with TIMI 3 flow restored."
                        },
                        {
                            "treatment_name": "Telemetry Monitoring & Titration",
                            "duration": "7 days",
                            "treatment_notes": "Continuous ECG monitoring; initiated dual antiplatelet therapy."
                        }
                    ],
                    medications_at_discharge=[
                        {
                            "medication_name": "Aspirin",
                            "dosage": "81 mg",
                            "frequency": "Once daily",
                            "duration": "Indefinite"
                        },
                        {
                            "medication_name": "Ticagrelor",
                            "dosage": "90 mg",
                            "frequency": "Twice daily",
                            "duration": "12 months"
                        },
                        {
                            "medication_name": "Atorvastatin",
                            "dosage": "80 mg",
                            "frequency": "Once daily at bedtime",
                            "duration": "Ongoing"
                        },
                        {
                            "medication_name": "Metoprolol Succinate",
                            "dosage": "50 mg",
                            "frequency": "Once daily",
                            "duration": "Ongoing"
                        }
                    ],
                    discharge_instructions=[
                        {"instruction": "Avoid heavy lifting greater than 10 lbs for 2 weeks."},
                        {"instruction": "Inspect right groin puncture site daily for hematoma or active bleeding."},
                        {"instruction": "Record blood pressure and heart rate twice daily before morning medications."}
                    ],
                    follow_up_appointments=[
                        {
                            "date": "2026-09-14",
                            "department": "Cardiology",
                            "provider": "Dr. Sarah Jenkins"
                        },
                        {
                            "date": "2026-10-05",
                            "department": "Cardiac Rehabilitation",
                            "provider": "Rehab Team Clinic B"
                        }
                    ],
                    responsible_physician={"name": "Dr. Sarah Jenkins", "contact": "+1 (555) 019-2834"},
                    additional_notes=[
                        {"note": "Patient exhibits baseline mild anxiety regarding recurrent chest sensations."},
                        {"note": "Caretaker trained on home pulse oximeter and automated BP cuff operation."}
                    ],
                    caretaker={"name": "Thomas Vance", "contact": "+1 (555) 234-5678", "relationship": "Spouse"},
                    created_at=datetime(2026, 8, 30, 10, 15, 0)
                ),
                "alerts": [
                    Alert(
                        patient_id="PT-904",
                        content="Critical drop in SpO2: 84% at resting state. Requires immediate assessment.",
                        priority=AlertPriority.CRITICAL,
                        created_at=datetime(2026, 9, 6, 18, 50, 0)
                    )
                ],
                "reminders": [
                    Reminder(
                        patient_id="PT-904",
                        frequency=ReminderFrequency.DAILY,
                        time="08:00",
                        content="Take Aspirin 81mg and Ticagrelor 90mg with breakfast.",
                        created_at=datetime(2026, 8, 30, 11, 0, 0)
                    ),
                    Reminder(
                        patient_id="PT-904",
                        frequency=ReminderFrequency.DAILY,
                        time="20:00",
                        content="Take Ticagrelor 90mg and Atorvastatin 80mg.",
                        created_at=datetime(2026, 8, 30, 11, 0, 0)
                    )
                ],
                "monitors": [
                    Monitor(
                        patient_id="PT-904",
                        frequency=MonitorFrequency.DAILY,
                        input_type=InputType.IMAGE,
                        time="10:00",
                        instructions="Take a well-lit photo of the right femoral access puncture site.",
                        things_to_evaluate="Check for expanding hematoma, active bleeding, spreading erythema, or purulence.",
                        trigger_alert_if="Erythema exceeds 2cm from puncture site, swelling palpated, or visible hematoma enlargement.",
                        created_at=datetime(2026, 8, 30, 11, 30, 0)
                    )
                ],
                "past_reminders": [
                    PastReminderEvent(
                        patient_id="PT-904",
                        content="Morning antiplatelet dose confirmation.",
                        resolved_or_not=True,
                        created_at=datetime(2026, 9, 6, 8, 12, 0)
                    )
                ],
                "past_monitors": [
                    PastMonitorEvent(
                        patient_id="PT-904",
                        input_given="/uploads/PT-904/groin_day6.jpg",
                        remark="Puncture site clean, minimal residual bruising, no signs of infection or pseudoaneurysm.",
                        alert_triggered_or_not=False,
                        created_at=datetime(2026, 9, 5, 10, 14, 0)
                    )
                ]
            },
            {
                "patient": Patient(
                    patient_id="PT-882",
                    name="Marcus Holloway",
                    age=54,
                    gender="Male",
                    admission_date=date(2026, 8, 25),
                    discharge_date=date(2026, 8, 28),
                    primary_diagnosis="Hypertensive Emergency resolved, Essential Hypertension Stage II",
                    hospital_course_description="Admitted with acute headache, blurred vision, and initial blood pressure of 218/124 mmHg. Treated with IV Nicardipine infusion in ICU step-down with gradual controlled reduction. Successfully transitioned to oral triple-therapy regimen.",
                    treatment_summary=[
                        {
                            "treatment_name": "Intravenous Antihypertensive Titration",
                            "duration": "24 hours",
                            "treatment_notes": "Nicardipine infusion titrated to maintain MAP decrease of 20% over first 6 hours."
                        },
                        {
                            "treatment_name": "Oral Regimen Conversion & Renal Monitoring",
                            "duration": "2 days",
                            "treatment_notes": "Serum creatinine remained baseline at 1.1 mg/dL; transitioned to Amlodipine + Losartan."
                        }
                    ],
                    medications_at_discharge=[
                        {
                            "medication_name": "Amlodipine",
                            "dosage": "10 mg",
                            "frequency": "Once daily in the morning",
                            "duration": "Ongoing"
                        },
                        {
                            "medication_name": "Losartan",
                            "dosage": "100 mg",
                            "frequency": "Once daily in the evening",
                            "duration": "Ongoing"
                        },
                        {
                            "medication_name": "Chlorthalidone",
                            "dosage": "25 mg",
                            "frequency": "Once daily with breakfast",
                            "duration": "Ongoing"
                        }
                    ],
                    discharge_instructions=[
                        {"instruction": "Maintain strict low-sodium dietary restriction (<2,000 mg/day)."},
                        {"instruction": "Log blood pressure morning and evening in the app."},
                        {"instruction": "Seek emergency care if systolic blood pressure exceeds 180 mmHg or diastolic exceeds 110 mmHg with acute symptoms."}
                    ],
                    follow_up_appointments=[
                        {
                            "date": "2026-09-08",
                            "department": "Internal Medicine",
                            "provider": "Dr. Ronald Patel"
                        }
                    ],
                    responsible_physician={"name": "Dr. Ronald Patel", "contact": "+1 (555) 014-9821"},
                    additional_notes=[
                        {"note": "Patient had self-discontinued previous antihypertensive medications 3 months prior."}
                    ],
                    caretaker={"name": "Denise Holloway", "contact": "+1 (555) 876-5432", "relationship": "Sister"},
                    created_at=datetime(2026, 8, 28, 14, 40, 0)
                ),
                "alerts": [
                    Alert(
                        patient_id="PT-882",
                        content="Acute systolic blood pressure spike detected: 178/95 mmHg.",
                        priority=AlertPriority.CRITICAL,
                        created_at=datetime(2026, 9, 6, 18, 42, 0)
                    )
                ],
                "reminders": [
                    Reminder(
                        patient_id="PT-882",
                        frequency=ReminderFrequency.DAILY,
                        time="07:30",
                        content="Take Amlodipine 10mg and Chlorthalidone 25mg.",
                        created_at=datetime(2026, 8, 28, 15, 0, 0)
                    ),
                    Reminder(
                        patient_id="PT-882",
                        frequency=ReminderFrequency.DAILY,
                        time="19:30",
                        content="Take Losartan 100mg.",
                        created_at=datetime(2026, 8, 28, 15, 0, 0)
                    )
                ],
                "monitors": [
                    Monitor(
                        patient_id="PT-882",
                        frequency=MonitorFrequency.DAILY,
                        input_type=InputType.IMAGE,
                        time="08:00",
                        instructions="Capture a clear digital photo of the automated BP monitor LCD screen after sitting resting for 5 minutes.",
                        things_to_evaluate="Evaluate systolic, diastolic, and pulse readouts from device display.",
                        trigger_alert_if="Systolic >= 170 mmHg or Diastolic >= 105 mmHg.",
                        created_at=datetime(2026, 8, 28, 15, 30, 0)
                    )
                ],
                "past_reminders": [
                    PastReminderEvent(
                        patient_id="PT-882",
                        content="Evening Losartan dose confirmation.",
                        resolved_or_not=True,
                        created_at=datetime(2026, 9, 5, 19, 45, 0)
                    )
                ],
                "past_monitors": [
                    PastMonitorEvent(
                        patient_id="PT-882",
                        input_given="/uploads/PT-882/bp_reading_sept06.jpg",
                        remark="Blood pressure readout shows 178/95 mmHg, triggering threshold alert.",
                        alert_triggered_or_not=True,
                        created_at=datetime(2026, 9, 6, 18, 42, 0)
                    )
                ]
            },
            {
                "patient": Patient(
                    patient_id="PT-765",
                    name="Sophia Reyes",
                    age=42,
                    gender="Female",
                    admission_date=date(2026, 8, 21),
                    discharge_date=date(2026, 8, 24),
                    primary_diagnosis="Supraventricular Tachycardia (Ablated), Hypokalemia",
                    hospital_course_description="Recurrent episodes of paroxysmal AV nodal reentrant tachycardia (AVNRT) refractory to medical management. Underwent elective electrophysiology study and successful slow-pathway radiofrequency catheter ablation. Replaced potassium orally.",
                    treatment_summary=[
                        {
                            "treatment_name": "Slow Pathway RF Catheter Ablation",
                            "duration": "1 day",
                            "treatment_notes": "Successful ablation with post-procedure non-inducibility of AVNRT."
                        }
                    ],
                    medications_at_discharge=[
                        {
                            "medication_name": "Metoprolol Tartrate",
                            "dosage": "25 mg",
                            "frequency": "Twice daily with meals",
                            "duration": "4 weeks"
                        },
                        {
                            "medication_name": "Potassium Chloride ER",
                            "dosage": "20 mEq",
                            "frequency": "Once daily with food",
                            "duration": "14 days"
                        }
                    ],
                    discharge_instructions=[
                        {"instruction": "Refrain from strenuous workouts and running for 10 days."},
                        {"instruction": "Log any feelings of fluttering or skipped beats immediately."}
                    ],
                    follow_up_appointments=[
                        {
                            "date": "2026-09-22",
                            "department": "Electrophysiology Clinic",
                            "provider": "Dr. Kevin Zhang"
                        }
                    ],
                    responsible_physician={"name": "Dr. Kevin Zhang", "contact": "+1 (555) 017-3312"},
                    additional_notes=[
                        {"note": "Patient has family history of thyroid dysfunction; TSH within normal limits during admission."}
                    ],
                    caretaker={"name": "Carlos Reyes", "contact": "+1 (555) 345-6789", "relationship": "Brother"},
                    created_at=datetime(2026, 8, 24, 9, 0, 0)
                ),
                "alerts": [
                    Alert(
                        patient_id="PT-765",
                        content="Missed scheduled evening medication: Metoprolol 25mg.",
                        priority=AlertPriority.HIGH,
                        created_at=datetime(2026, 9, 6, 18, 15, 0)
                    )
                ],
                "reminders": [
                    Reminder(
                        patient_id="PT-765",
                        frequency=ReminderFrequency.DAILY,
                        time="08:30",
                        content="Take Metoprolol Tartrate 25mg and Potassium Chloride 20 mEq.",
                        created_at=datetime(2026, 8, 24, 10, 0, 0)
                    ),
                    Reminder(
                        patient_id="PT-765",
                        frequency=ReminderFrequency.DAILY,
                        time="20:30",
                        content="Take Metoprolol Tartrate 25mg.",
                        created_at=datetime(2026, 8, 24, 10, 0, 0)
                    )
                ],
                "monitors": [
                    Monitor(
                        patient_id="PT-765",
                        frequency=MonitorFrequency.DAILY,
                        input_type=InputType.VIDEO,
                        time="09:00",
                        instructions="Record a 15-second video recording pulse palpation at the radial artery or smartwatch telemetry rhythm screen.",
                        things_to_evaluate="Rhythm regularity, heart rate estimate between 60-100 bpm.",
                        trigger_alert_if="Irregular beats detected or heart rate sustained above 110 bpm.",
                        created_at=datetime(2026, 8, 24, 10, 30, 0)
                    )
                ],
                "past_reminders": [
                    PastReminderEvent(
                        patient_id="PT-765",
                        content="Morning beta blocker dose.",
                        resolved_or_not=True,
                        created_at=datetime(2026, 9, 6, 8, 35, 0)
                    )
                ],
                "past_monitors": []
            },
            {
                "patient": Patient(
                    patient_id="PT-630",
                    name="Arthur Pendelton",
                    age=73,
                    gender="Male",
                    admission_date=date(2026, 8, 14),
                    discharge_date=date(2026, 8, 20),
                    primary_diagnosis="Type 2 Diabetes Mellitus with hyperosmolar state, Diabetic Nephropathy Stage 3a",
                    hospital_course_description="Presented with altered sensorium, severe dehydration, and serum glucose of 740 mg/dL with serum osmolality 335 mOsm/kg. Aggressively rehydrated with normal saline and IV insulin infusion. Mentation returned to baseline by hospital day 3. Diabetic educator consulted.",
                    treatment_summary=[
                        {
                            "treatment_name": "Intravenous Fluid Resuscitation & Insulin Protocol",
                            "duration": "3 days",
                            "treatment_notes": "6 liters isotonic saline followed by 0.45% NaCl + D5W with low-dose regular insulin infusion."
                        },
                        {
                            "treatment_name": "Basal-Bolus Regimen Transition",
                            "duration": "3 days",
                            "treatment_notes": "Established Glargine baseline at 24 units bedtime and Lispro sliding scale."
                        }
                    ],
                    medications_at_discharge=[
                        {
                            "medication_name": "Insulin Glargine (Lantus)",
                            "dosage": "24 units",
                            "frequency": "Once daily at 21:00",
                            "duration": "Ongoing"
                        },
                        {
                            "medication_name": "Insulin Lispro (Humalog)",
                            "dosage": "4 units",
                            "frequency": "Three times daily before meals",
                            "duration": "Ongoing"
                        },
                        {
                            "medication_name": "Empagliflozin",
                            "dosage": "10 mg",
                            "frequency": "Once daily in morning",
                            "duration": "Ongoing"
                        }
                    ],
                    discharge_instructions=[
                        {"instruction": "Check fingerstick glucose before every meal and at bedtime."},
                        {"instruction": "Keep oral glucose tablets or juice box accessible at bedside at all times."},
                        {"instruction": "Inspect bilateral soles and interdigital spaces of feet daily for sores or skin breakdown."}
                    ],
                    follow_up_appointments=[
                        {
                            "date": "2026-09-10",
                            "department": "Endocrinology",
                            "provider": "Dr. Anita Desai"
                        },
                        {
                            "date": "2026-09-28",
                            "department": "Podiatry",
                            "provider": "Foot & Ankle Specialists"
                        }
                    ],
                    responsible_physician={"name": "Dr. Anita Desai", "contact": "+1 (555) 012-7788"},
                    additional_notes=[
                        {"note": "Patient requires large font instruction labels due to mild diabetic retinopathy."}
                    ],
                    caretaker={"name": "Margaret Pendelton", "contact": "+1 (555) 987-6543", "relationship": "Daughter"},
                    created_at=datetime(2026, 8, 20, 11, 20, 0)
                ),
                "alerts": [
                    Alert(
                        patient_id="PT-630",
                        content="Continuous glucose monitor indicates persistent hypoglycemia (<60 mg/dL).",
                        priority=AlertPriority.CRITICAL,
                        created_at=datetime(2026, 9, 6, 17, 30, 0)
                    )
                ],
                "reminders": [
                    Reminder(
                        patient_id="PT-630",
                        frequency=ReminderFrequency.DAILY,
                        time="07:00",
                        content="Check fasting blood glucose and take Empagliflozin 10mg.",
                        created_at=datetime(2026, 8, 20, 12, 0, 0)
                    ),
                    Reminder(
                        patient_id="PT-630",
                        frequency=ReminderFrequency.DAILY,
                        time="21:00",
                        content="Administer 24 units Insulin Glargine subcutaneously.",
                        created_at=datetime(2026, 8, 20, 12, 0, 0)
                    )
                ],
                "monitors": [
                    Monitor(
                        patient_id="PT-630",
                        frequency=MonitorFrequency.DAILY,
                        input_type=InputType.IMAGE,
                        time="20:00",
                        instructions="Take clear photos of the soles and heels of both feet under bright room lighting.",
                        things_to_evaluate="Examine skin integrity, redness, blisters, pressure sores, or ulcerations.",
                        trigger_alert_if="New redness, skin tear, blister, or drainage noted on either foot.",
                        created_at=datetime(2026, 8, 20, 12, 30, 0)
                    )
                ],
                "past_reminders": [
                    PastReminderEvent(
                        patient_id="PT-630",
                        content="Bedtime basal insulin injection confirmation.",
                        resolved_or_not=True,
                        created_at=datetime(2026, 9, 5, 21, 10, 0)
                    )
                ],
                "past_monitors": [
                    PastMonitorEvent(
                        patient_id="PT-630",
                        input_given="/uploads/PT-630/feet_check_sept05.jpg",
                        remark="Bilateral plantar skin intact, no erythema or pressure lesions observed.",
                        alert_triggered_or_not=False,
                        created_at=datetime(2026, 9, 5, 20, 15, 0)
                    )
                ]
            },
            {
                "patient": Patient(
                    patient_id="PT-512",
                    name="Amara Chen",
                    age=36,
                    gender="Female",
                    admission_date=date(2026, 8, 9),
                    discharge_date=date(2026, 8, 15),
                    primary_diagnosis="Community-Acquired Pneumonia (Resolved), Moderate Persistent Asthma Exacerbation",
                    hospital_course_description="Presented with fever of 39.1°C, productive cough, left lower lobe consolidation on chest radiography, and wheezing. Responded well to IV Ceftriaxone and Azithromycin plus systemic methylprednisolone. De-escalated to oral antibiotics and completed 7-day course.",
                    treatment_summary=[
                        {
                            "treatment_name": "Intravenous Antibiotic & Steroid Therapy",
                            "duration": "4 days",
                            "treatment_notes": "Ceftriaxone 1g daily + Azithromycin 500mg IV; oral switch on day 5."
                        },
                        {
                            "treatment_name": "Bronchodilator Nebulization",
                            "duration": "5 days",
                            "treatment_notes": "Albuterol/Ipratropium q4h transitioned to maintenance inhaler."
                        }
                    ],
                    medications_at_discharge=[
                        {
                            "medication_name": "Fluticasone / Salmeterol (Advair Diskus 250/50)",
                            "dosage": "1 inhalation",
                            "frequency": "Twice daily",
                            "duration": "Ongoing"
                        },
                        {
                            "medication_name": "Albuterol HFA Inhaler",
                            "dosage": "2 puffs",
                            "frequency": "Every 4-6 hours as needed for shortness of breath",
                            "duration": "PRN"
                        },
                        {
                            "medication_name": "Prednisone Taper",
                            "dosage": "20 mg daily for 3 days, then 10 mg daily for 3 days",
                            "frequency": "Once daily with breakfast",
                            "duration": "6 days"
                        }
                    ],
                    discharge_instructions=[
                        {"instruction": "Rinse mouth thoroughly with water after using Advair inhaler."},
                        {"instruction": "Perform peak flow measurement every morning and record the highest of three attempts."},
                        {"instruction": "Avoid contact with smoke, chemical fumes, and airborne allergens."}
                    ],
                    follow_up_appointments=[
                        {
                            "date": "2026-09-12",
                            "department": "Pulmonology",
                            "provider": "Dr. Elena Rostova"
                        }
                    ],
                    responsible_physician={"name": "Dr. Elena Rostova", "contact": "+1 (555) 015-4429"},
                    additional_notes=[
                        {"note": "Patient demonstrated good spacer technique before discharge."}
                    ],
                    caretaker={"name": "David Chen", "contact": "+1 (555) 432-1098", "relationship": "Spouse"},
                    created_at=datetime(2026, 8, 15, 8, 30, 0)
                ),
                "alerts": [],
                "reminders": [
                    Reminder(
                        patient_id="PT-512",
                        frequency=ReminderFrequency.DAILY,
                        time="08:00",
                        content="Inhale Advair 250/50 (1 puff) and rinse mouth.",
                        created_at=datetime(2026, 8, 15, 9, 0, 0)
                    ),
                    Reminder(
                        patient_id="PT-512",
                        frequency=ReminderFrequency.DAILY,
                        time="20:00",
                        content="Inhale Advair 250/50 (1 puff) and rinse mouth.",
                        created_at=datetime(2026, 8, 15, 9, 0, 0)
                    )
                ],
                "monitors": [
                    Monitor(
                        patient_id="PT-512",
                        frequency=MonitorFrequency.DAILY,
                        input_type=InputType.IMAGE,
                        time="08:15",
                        instructions="Take a photograph of your mechanical peak flow meter showing the indicator position after your morning test.",
                        things_to_evaluate="Evaluate peak expiratory flow rate (PEFR) against personal best threshold (420 L/min).",
                        trigger_alert_if="Peak flow value falls below 320 L/min (yellow/red zone).",
                        created_at=datetime(2026, 8, 15, 9, 30, 0)
                    )
                ],
                "past_reminders": [
                    PastReminderEvent(
                        patient_id="PT-512",
                        content="Morning inhaler maintenance dose.",
                        resolved_or_not=True,
                        created_at=datetime(2026, 9, 6, 8, 5, 0)
                    )
                ],
                "past_monitors": [
                    PastMonitorEvent(
                        patient_id="PT-512",
                        input_given="/uploads/PT-512/pefr_sept06.jpg",
                        remark="Peak flow meter shows 390 L/min. Patient is in the green zone.",
                        alert_triggered_or_not=False,
                        created_at=datetime(2026, 9, 6, 8, 20, 0)
                    )
                ]
            }
        ]

        for record in patients_data:
            patient_obj = record["patient"]
            db.add(patient_obj)
            db.flush()  # Ensures patient_id primary key exists in session

            for alert in record["alerts"]:
                db.add(alert)

            for reminder in record["reminders"]:
                db.add(reminder)

            for monitor in record["monitors"]:
                db.add(monitor)

            for past_rem in record["past_reminders"]:
                db.add(past_rem)

            for past_mon in record["past_monitors"]:
                db.add(past_mon)

        db.commit()
        print(f"Successfully seeded {len(patients_data)} patients and their related clinical entities.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed()
