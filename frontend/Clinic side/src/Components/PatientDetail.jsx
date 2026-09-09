import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useForm, useFieldArray } from "react-hook-form";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Edit3,
  Check,
  X,
  User,
  Pill,
  Bell,
  Activity,
  ChevronRight,
  Plus,
  Trash2,
  Clock,
  AlertCircle,
  FileText,
  CalendarCheck,
  ShieldAlert,
  Camera,
  Video,
  AlertTriangle,
  BellRing,
  ShieldCheck,
} from "lucide-react";
import axios from "axios";

// ==========================================
// SEPARATE API STUBS
// ==========================================

export async function fetchPatientDetail(patientId) {
  // TODO: Replace with Axios call (e.g. const res = await axios.get(`http://localhost:8000/api/v1/patients/${patientId}`); return res.data;)
  const { data } = await axios.get(`/api/api/v1/patients/${patientId}`);
  return data;
}

export async function updatePatientDetail(patientId, payload) {
  // TODO: Replace with Axios call (e.g., await axios.put(`http://localhost:8000/api/v1/patients/${patientId}`, payload);)
  const { data } = await axios.put(
    `/api/api/v1/patients/${patientId}`,
    payload
  );
  return data;
}

function useAnimatedNavigate() {
  const navigate = useNavigate();
  const isNavigating = useRef(false);

  const animatedNavigate = (to, delay = 160) => {
    if (isNavigating.current) return;
    isNavigating.current = true;
    setTimeout(() => {
      navigate(to);
    }, delay);
  };

  return animatedNavigate;
}

const pageVariants = {
  initial: { opacity: 0, y: 14 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: [0.25, 1, 0.5, 1] },
  },
  exit: { opacity: 0, y: -10, transition: { duration: 0.2 } },
};

export default function PatientDetail() {
  const { id } = useParams();
  const navigate = useAnimatedNavigate();

  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [patientData, setPatientData] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const { register, control, handleSubmit, reset } = useForm({
    defaultValues: {
      name: "",
      age: "",
      gender: "",
      admission_date: "",
      discharge_date: "",
      primary_diagnosis: "",
      hospital_course_description: "",
      physician_name: "",
      physician_contact: "",
      caretaker_name: "",
      caretaker_contact: "",
      caretaker_relationship: "",
      reminders: [],
      monitors: [],
    },
  });

  const {
    fields: reminderFields,
    append: appendReminder,
    remove: removeReminder,
  } = useFieldArray({ control, name: "reminders" });

  const {
    fields: monitorFields,
    append: appendMonitor,
    remove: removeMonitor,
  } = useFieldArray({ control, name: "monitors" });

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const data = await fetchPatientDetail(id);
        if (isMounted) {
          setPatientData(data);
          reset({
            name: data.name,
            age: data.age,
            gender: data.gender,
            admission_date: data.admission_date || "",
            discharge_date: data.discharge_date || "",
            primary_diagnosis: data.primary_diagnosis || "",
            hospital_course_description: data.hospital_course_description || "",
            physician_name: data.responsible_physician?.name || "",
            physician_contact: data.responsible_physician?.contact || "",
            caretaker_name: data.caretaker?.name || "",
            caretaker_contact: data.caretaker?.contact || "",
            caretaker_relationship: data.caretaker?.relationship || "",
            reminders: data.reminders || [],
            monitors: data.monitors || [],
          });
        }
      } catch (err) {
        console.error("Failed to load patient detail:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [id, reset]);

  const toggleEditMode = () => {
    if (isEditing && patientData) {
      reset({
        name: patientData.name,
        age: patientData.age,
        gender: patientData.gender,
        admission_date: patientData.admission_date || "",
        discharge_date: patientData.discharge_date || "",
        primary_diagnosis: patientData.primary_diagnosis || "",
        hospital_course_description:
          patientData.hospital_course_description || "",
        physician_name: patientData.responsible_physician?.name || "",
        physician_contact: patientData.responsible_physician?.contact || "",
        caretaker_name: patientData.caretaker?.name || "",
        caretaker_contact: patientData.caretaker?.contact || "",
        caretaker_relationship: patientData.caretaker?.relationship || "",
        reminders: patientData.reminders || [],
        monitors: patientData.monitors || [],
      });
    }
    setIsEditing(!isEditing);
  };

  const onSaveForm = async (formData) => {
    setIsSaving(true);
    try {
      const updatedPayload = {
        ...patientData,
        name: formData.name,
        age: parseInt(formData.age, 10),
        gender: formData.gender,
        admission_date: formData.admission_date,
        discharge_date: formData.discharge_date,
        primary_diagnosis: formData.primary_diagnosis,
        hospital_course_description: formData.hospital_course_description,
        responsible_physician: {
          name: formData.physician_name,
          contact: formData.physician_contact,
        },
        caretaker: {
          name: formData.caretaker_name,
          contact: formData.caretaker_contact,
          relationship: formData.caretaker_relationship,
        },
        reminders: formData.reminders,
        monitors: formData.monitors,
      };

      await updatePatientDetail(id, updatedPayload);
      setPatientData(updatedPayload);
      setIsEditing(false);
    } catch (err) {
      console.error("Failed to update patient:", err);
      alert("Could not save changes. Please try again.");
    } finally {
      setIsSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 flex flex-col items-center justify-center text-slate-400 gap-3">
        <Clock className="w-8 h-8 animate-spin text-indigo-600" />
        <span className="text-sm font-medium">Loading clinical record...</span>
      </div>
    );
  }

  if (!patientData) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-2" />
        <h2 className="text-lg font-bold text-slate-800">Patient Not Found</h2>
        <p className="text-xs text-slate-500 mt-1">
          No record exists for identifier:{" "}
          <span className="font-mono">{id}</span>
        </p>
        <button
          onClick={() => navigate("/patients")}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white text-xs font-semibold rounded-xl"
        >
          Return to Registry
        </button>
      </div>
    );
  }

  const displayedReminders = (patientData.reminders || []).slice(0, 3);
  const displayedMonitors = (patientData.monitors || []).slice(0, 3);
  const patientAlerts = (patientData.alerts || []).filter(
    (alert) => alert.patientId === (id || patientData.patient_id)
  );

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="max-w-4xl mx-auto px-4 py-8 flex flex-col gap-6"
    >
      {/* HEADER & TOP EDIT TOGGLE */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.05, x: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate("/patients")}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 shadow-sm transition-colors"
            title="Back to Patients List"
          >
            <ArrowLeft className="w-5 h-5" />
          </motion.button>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-2xl font-bold text-slate-900">
                {patientData.name}
              </h1>
              <span className="text-xs font-mono font-bold px-2.5 py-0.5 rounded-full bg-slate-100 text-slate-700">
                {patientData.patient_id}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              {patientData.age} yrs • {patientData.gender} • Discharged on{" "}
              {patientData.discharge_date || "N/A"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          {isEditing ? (
            <>
              <button
                type="button"
                onClick={toggleEditMode}
                className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 text-xs font-semibold shadow-sm transition-all"
              >
                <X className="w-4 h-4 text-slate-400" />
                Cancel
              </button>
              <button
                type="button"
                disabled={isSaving}
                onClick={handleSubmit(onSaveForm)}
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-semibold shadow-sm transition-all"
              >
                <Check className="w-4 h-4" />
                {isSaving ? "Saving..." : "Save Changes"}
              </button>
            </>
          ) : (
            <motion.button
              whileHover={{ y: -2 }}
              whileTap={{ scale: 0.97 }}
              onClick={toggleEditMode}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-50 border border-indigo-200 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold shadow-sm transition-all"
            >
              <Edit3 className="w-4 h-4 text-indigo-600" />
              Edit Details
            </motion.button>
          )}
        </div>
      </div>

      {/* FORM & MAIN SECTIONS */}
      <form onSubmit={handleSubmit(onSaveForm)} className="space-y-6">
        {/* SECTION 1: ALL PATIENT DETAILS */}
        <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-6">
          <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
            <User className="w-5 h-5 text-indigo-600" />
            <h2 className="text-lg font-bold text-slate-800">
              Patient Details & Clinical Course
            </h2>
          </div>

          {isEditing ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    {...register("name", { required: true })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Age
                  </label>
                  <input
                    type="number"
                    {...register("age", { required: true })}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Gender
                  </label>
                  <select
                    {...register("gender")}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-white"
                  >
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Admission Date
                  </label>
                  <input
                    type="date"
                    {...register("admission_date")}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1">
                    Discharge Date
                  </label>
                  <input
                    type="date"
                    {...register("discharge_date")}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Primary Diagnosis
                </label>
                <input
                  type="text"
                  {...register("primary_diagnosis", { required: true })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Hospital Course Description
                </label>
                <textarea
                  rows={3}
                  {...register("hospital_course_description")}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-100">
                <div className="space-y-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Caretaker Information
                  </span>
                  <input
                    type="text"
                    placeholder="Name"
                    {...register("caretaker_name")}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Contact Number"
                    {...register("caretaker_contact")}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Relationship"
                    {...register("caretaker_relationship")}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none"
                  />
                </div>

                <div className="space-y-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                    Attending Physician
                  </span>
                  <input
                    type="text"
                    placeholder="Doctor Name"
                    {...register("physician_name")}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Phone or Clinic Contact"
                    {...register("physician_contact")}
                    className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none"
                  />
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6 text-xs text-slate-600">
              <div className="space-y-3">
                <div>
                  <span className="text-slate-400 font-semibold block text-[11px] uppercase tracking-wider">
                    Primary Diagnosis
                  </span>
                  <p className="text-sm font-bold text-slate-900 mt-0.5">
                    {patientData.primary_diagnosis}
                  </p>
                </div>

                <div>
                  <span className="text-slate-400 font-semibold block text-[11px] uppercase tracking-wider">
                    Hospital Course Summary
                  </span>
                  <p className="text-xs text-slate-700 mt-1 leading-relaxed bg-slate-50/70 p-3 rounded-xl border border-slate-100">
                    {patientData.hospital_course_description}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 p-3.5 bg-slate-50/70 rounded-xl border border-slate-100">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">
                    Admission Date
                  </span>
                  <span className="font-semibold text-slate-800">
                    {patientData.admission_date || "N/A"}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">
                    Discharge Date
                  </span>
                  <span className="font-semibold text-slate-800">
                    {patientData.discharge_date || "N/A"}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">
                    Primary Caretaker
                  </span>
                  <span className="font-semibold text-slate-800 block">
                    {patientData.caretaker?.name} (
                    {patientData.caretaker?.relationship})
                  </span>
                  <span className="text-slate-500 text-[11px]">
                    {patientData.caretaker?.contact}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-bold">
                    Responsible Doctor
                  </span>
                  <span className="font-semibold text-slate-800 block">
                    {patientData.responsible_physician?.name}
                  </span>
                  <span className="text-slate-500 text-[11px]">
                    {patientData.responsible_physician?.contact}
                  </span>
                </div>
              </div>

              {patientData.medications_at_discharge?.length > 0 && (
                <div className="space-y-2">
                  <span className="text-slate-400 font-semibold block text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                    <Pill className="w-3.5 h-3.5 text-indigo-600" /> Medications
                    at Discharge
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {patientData.medications_at_discharge.map((med, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-white rounded-xl border border-slate-200 flex flex-col justify-between shadow-2xs"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-slate-900">
                            {med.medication_name}
                          </span>
                          <span className="text-[11px] font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">
                            {med.dosage}
                          </span>
                        </div>
                        <div className="text-[11px] text-slate-500 mt-1">
                          {med.frequency} •{" "}
                          <span className="italic">{med.duration}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {patientData.discharge_instructions?.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-slate-400 font-semibold block text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                      <FileText className="w-3.5 h-3.5 text-indigo-600" />{" "}
                      Instructions
                    </span>
                    <ul className="space-y-1.5 list-disc list-inside text-slate-700">
                      {patientData.discharge_instructions.map((inst, idx) => (
                        <li key={idx} className="leading-normal">
                          {inst.instruction}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {patientData.follow_up_appointments?.length > 0 && (
                  <div className="space-y-1.5">
                    <span className="text-slate-400 font-semibold block text-[11px] uppercase tracking-wider flex items-center gap-1.5">
                      <CalendarCheck className="w-3.5 h-3.5 text-indigo-600" />{" "}
                      Appointments
                    </span>
                    <div className="space-y-1.5">
                      {patientData.follow_up_appointments.map((app, idx) => (
                        <div
                          key={idx}
                          className="p-2 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between"
                        >
                          <div>
                            <span className="font-semibold text-slate-800 block">
                              {app.department}
                            </span>
                            <span className="text-[11px] text-slate-500">
                              {app.provider}
                            </span>
                          </div>
                          <span className="text-[11px] font-mono font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                            {app.date}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>

        {/* SECTION 2: REMINDERS */}
        <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div
              onClick={() =>
                !isEditing && navigate(`/patients/${id}/reminders`)
              }
              className={`flex items-center gap-2.5 ${
                !isEditing ? "cursor-pointer group select-none" : ""
              }`}
            >
              <div className="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                <Bell className="w-4 h-4" />
              </div>
              <h2 className="text-lg font-bold text-slate-800 group-hover:text-indigo-600 transition-colors flex items-center gap-1.5">
                Reminders
                <span className="text-xs font-semibold text-slate-400">
                  (
                  {
                    (isEditing ? reminderFields : patientData.reminders || [])
                      .length
                  }
                  )
                </span>
                {!isEditing && (
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 group-hover:text-indigo-600 transition-all" />
                )}
              </h2>
            </div>

            {isEditing ? (
              <button
                type="button"
                onClick={() =>
                  appendReminder({
                    frequency: "daily",
                    time: "08:00",
                    content: "",
                  })
                }
                className="flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 bg-indigo-50 px-2.5 py-1.5 rounded-lg transition-colors"
              >
                <Plus className="w-3.5 h-3.5" /> Add Reminder
              </button>
            ) : (
              <button
                type="button"
                onClick={() => navigate(`/patients/${id}/reminders`)}
                className="text-xs font-semibold text-slate-400 hover:text-indigo-600 transition-colors"
              >
                View Past & All Reminders
              </button>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-3">
              {reminderFields.map((field, idx) => (
                <div
                  key={field.id}
                  className="p-3 bg-slate-50 rounded-xl border border-slate-200 flex flex-col sm:flex-row items-start sm:items-center gap-2.5"
                >
                  <select
                    {...register(`reminders.${idx}.frequency`)}
                    className="px-2 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                  >
                    <option value="once">Once</option>
                    <option value="daily">Daily</option>
                  </select>
                  <input
                    type="time"
                    {...register(`reminders.${idx}.time`, { required: true })}
                    className="px-2 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Content / instruction..."
                    {...register(`reminders.${idx}.content`, {
                      required: true,
                    })}
                    className="flex-1 w-full px-3 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => removeReminder(idx)}
                    className="p-1.5 text-slate-400 hover:text-red-500 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          ) : displayedReminders.length === 0 ? (
            <p className="text-xs text-slate-400 py-2">
              No active reminders configured.
            </p>
          ) : (
            <div className="space-y-2.5">
              {displayedReminders.map((reminder) => (
                <motion.div
                  key={reminder.id}
                  whileHover={{ y: -2, scale: 1.004 }}
                  whileTap={{ scale: 0.985 }}
                  onClick={() =>
                    navigate(`/patients/${id}/reminders/${reminder.id}`)
                  }
                  className="p-3.5 bg-slate-50/70 hover:bg-white border border-slate-200 hover:border-indigo-300 rounded-xl flex items-center justify-between cursor-pointer transition-all shadow-2xs group"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-indigo-50 text-indigo-600 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {reminder.time}
                    </span>
                    <div>
                      <p className="text-xs font-semibold text-slate-800 group-hover:text-indigo-600 transition-colors">
                        {reminder.content}
                      </p>
                      <span className="text-[10px] uppercase font-bold text-slate-400">
                        {reminder.frequency}
                      </span>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 group-hover:text-indigo-600 transition-all" />
                </motion.div>
              ))}
            </div>
          )}
        </section>

        {/* SECTION 3: MONITORS */}
        <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div
              onClick={() => !isEditing && navigate(`/patients/${id}/monitors`)}
              className={`flex items-center gap-2.5 ${
                !isEditing ? "cursor-pointer group select-none" : ""
              }`}
            >
              <div className="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                <Activity className="w-4 h-4" />
              </div>
              <h2 className="text-lg font-bold text-slate-800 group-hover:text-indigo-600 transition-colors flex items-center gap-1.5">
                Telemetry Monitors
                <span className="text-xs font-semibold text-slate-400">
                  (
                  {
                    (isEditing ? monitorFields : patientData.monitors || [])
                      .length
                  }
                  )
                </span>
                {!isEditing && (
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-0.5 group-hover:text-indigo-600 transition-all" />
                )}
              </h2>
            </div>

            {isEditing ? (
              <button
                type="button"
                onClick={() =>
                  appendMonitor({
                    frequency: "daily",
                    input_type: "image",
                    time: "09:00",
                    instructions: "",
                    things_to_evaluate: "",
                    trigger_alert_if: "",
                  })
                }
                className="flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700 bg-indigo-50 px-2.5 py-1.5 rounded-lg transition-colors"
              >
                <Plus className="w-3.5 h-3.5" /> Add Monitor
              </button>
            ) : (
              <button
                type="button"
                onClick={() => navigate(`/patients/${id}/monitors`)}
                className="text-xs font-semibold text-slate-400 hover:text-indigo-600 transition-colors"
              >
                View All Monitors
              </button>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-4">
              {monitorFields.map((field, idx) => (
                <div
                  key={field.id}
                  className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2.5"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold text-indigo-600 uppercase tracking-wider">
                      Monitor Protocol #{idx + 1}
                    </span>
                    <button
                      type="button"
                      onClick={() => removeMonitor(idx)}
                      className="text-slate-400 hover:text-red-500"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                    <select
                      {...register(`monitors.${idx}.frequency`)}
                      className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                    >
                      <option value="once">Once</option>
                      <option value="daily">Daily</option>
                      <option value="per_week">Per Week</option>
                      <option value="per_month">Per Month</option>
                      <option value="per_year">Per Year</option>
                    </select>

                    <select
                      {...register(`monitors.${idx}.input_type`)}
                      className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                    >
                      <option value="image">Image (Photo)</option>
                      <option value="video">Video</option>
                    </select>

                    <input
                      type="time"
                      {...register(`monitors.${idx}.time`, { required: true })}
                      className="px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                    />
                  </div>

                  <input
                    type="text"
                    placeholder="Instructions for patient..."
                    {...register(`monitors.${idx}.instructions`, {
                      required: true,
                    })}
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Things to evaluate..."
                    {...register(`monitors.${idx}.things_to_evaluate`, {
                      required: true,
                    })}
                    className="w-full px-3 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Trigger alert if..."
                    {...register(`monitors.${idx}.trigger_alert_if`, {
                      required: true,
                    })}
                    className="w-full px-3 py-1.5 rounded-lg border border-red-200 text-xs bg-white focus:outline-none text-red-800 placeholder-red-300"
                  />
                </div>
              ))}
            </div>
          ) : displayedMonitors.length === 0 ? (
            <p className="text-xs text-slate-400 py-2">
              No active monitors scheduled.
            </p>
          ) : (
            <div className="space-y-3">
              {displayedMonitors.map((monitor) => (
                <motion.div
                  key={monitor.id}
                  whileHover={{ y: -2, scale: 1.004 }}
                  whileTap={{ scale: 0.985 }}
                  onClick={() =>
                    navigate(`/patients/${id}/monitors/${monitor.id}`)
                  }
                  className="p-4 bg-slate-50/70 hover:bg-white border border-slate-200 hover:border-indigo-300 rounded-xl cursor-pointer transition-all shadow-2xs group flex flex-col gap-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="p-1 rounded bg-indigo-50 text-indigo-600">
                        {monitor.input_type === "video" ? (
                          <Video className="w-3.5 h-3.5" />
                        ) : (
                          <Camera className="w-3.5 h-3.5" />
                        )}
                      </span>
                      <span className="text-xs font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                        {monitor.instructions}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-xs">
                      <span className="font-mono text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded text-[11px] font-semibold">
                        {monitor.time} • {monitor.frequency}
                      </span>
                      <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 group-hover:text-indigo-600 transition-all" />
                    </div>
                  </div>

                  <div className="flex items-start gap-1.5 text-[11px] text-red-600 bg-red-50/60 p-2 rounded-lg border border-red-100">
                    <ShieldAlert className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                    <span>
                      <span className="font-semibold">Threshold:</span>{" "}
                      {monitor.trigger_alert_if}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </section>

        {/* SECTION 4: PATIENT ALERTS */}
        <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div className="flex items-center gap-2.5">
              <div className="p-1.5 bg-red-50 text-red-600 rounded-lg">
                <BellRing className="w-4 h-4" />
              </div>
              <h2 className="text-lg font-bold text-slate-800 flex items-center gap-1.5">
                Active & Recent Alerts
                <span className="text-xs font-semibold text-slate-400">
                  ({patientAlerts.length})
                </span>
              </h2>
            </div>
          </div>

          {patientAlerts.length === 0 ? (
            <div className="flex items-center gap-2 text-xs text-emerald-600 bg-emerald-50/70 px-4 py-3 rounded-xl border border-emerald-100">
              <ShieldCheck className="w-4 h-4 shrink-0" />
              <span>
                No active or unresolved alerts registered for this patient.
              </span>
            </div>
          ) : (
            <div className="space-y-3">
              {patientAlerts.map((alert) => {
                const isCritical = alert.priority?.toLowerCase() === "critical";

                return (
                  <div
                    key={alert.id}
                    className={`p-4 rounded-xl border transition-all shadow-2xs ${
                      isCritical
                        ? "bg-red-50/80 border-red-300"
                        : "bg-amber-50/60 border-amber-200"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5 mb-1.5">
                      <div className="flex items-center gap-2">
                        <AlertTriangle
                          className={`w-4 h-4 shrink-0 ${
                            isCritical
                              ? "text-red-600 animate-pulse"
                              : "text-amber-500"
                          }`}
                        />
                        <span className="text-xs font-mono font-bold text-slate-700">
                          {alert.id}
                        </span>
                        <span
                          className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                            isCritical
                              ? "bg-red-600 text-white"
                              : "bg-amber-100 text-amber-800"
                          }`}
                        >
                          {alert.priority}
                        </span>
                      </div>
                      <span className="text-[11px] text-slate-400">
                        {alert.timestamp}
                      </span>
                    </div>

                    <p
                      className={`text-xs ${
                        isCritical
                          ? "text-red-950 font-semibold"
                          : "text-slate-700"
                      }`}
                    >
                      {alert.content}
                    </p>
                  </div>
                );
              })}
            </div>
          )}
        </section>
      </form>
    </motion.div>
  );
}
