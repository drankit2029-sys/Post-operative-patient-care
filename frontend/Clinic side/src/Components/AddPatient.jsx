import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useForm, useFieldArray } from "react-hook-form";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowLeft,
  FileEdit,
  UploadCloud,
  Plus,
  Trash2,
  Bell,
  Activity,
  User,
  Stethoscope,
  Phone,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Calendar,
  Clock,
  Sparkles,
  FileText,
} from "lucide-react"; 
import axios from "axios";

// ==========================================
// SEPARATE API STUBS (Logic to be hooked up)
// ==========================================

// Stub: Send parsed/entered patient payload to backend
export async function createPatientRecord(payload) {
  
  const { data } = await axios.post('api/api/v1/patients', payload);
  return data;
  
}

// Stub: Send discharge summary image to backend for OCR/LLM entity extraction
export async function uploadAndParseDischargeSummary(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await axios.post(
    "api/api/v1/parse-discharge",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
}

// Animation configurations
const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: [0.25, 1, 0.5, 1] },
  },
  exit: { opacity: 0, y: -12, transition: { duration: 0.2 } },
};

export default function AddPatient() {
  const navigate = useNavigate();
  const [viewMode, setViewMode] = useState("select"); // 'select' | 'upload' | 'form'
  const [selectedFile, setSelectedFile] = useState(null);
  const [isParsing, setIsParsing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);
  const fileInputRef = useRef(null);

  const {
    register,
    control,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    defaultValues: {
      patient_id: "",
      name: "",
      age: "",
      gender: "Male",
      admission_date: "",
      discharge_date: "",
      primary_diagnosis: "",
      hospital_course_description: "",
      physician_name: "",
      physician_contact: "",
      caretaker_name: "",
      caretaker_contact: "",
      caretaker_relationship: "",
      medications_at_discharge: [
        { medication_name: "", dosage: "", frequency: "", duration: "" },
      ],
      discharge_instructions: [{ instruction: "" }],
      reminders: [{ frequency: "daily", time: "08:00", content: "" }],
      monitors: [
        {
          frequency: "daily",
          input_type: "image",
          time: "09:00",
          instructions: "",
          things_to_evaluate: "",
          trigger_alert_if: "",
        },
      ],
    },
  });

  // Dynamic form array managers
  const {
    fields: medFields,
    append: appendMed,
    remove: removeMed,
  } = useFieldArray({ control, name: "medications_at_discharge" });

  const {
    fields: instructionFields,
    append: appendInstruction,
    remove: removeInstruction,
  } = useFieldArray({ control, name: "discharge_instructions" });

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

  // Handle file selection & automated upload extraction
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setSelectedFile(file);
    setIsParsing(true);

    try {
      const extractedData = await uploadAndParseDischargeSummary(file);
      reset(extractedData);
      setViewMode("form");
    } catch (err) {
      console.error("Failed to parse summary:", err);
      alert("Unable to extract data from the document. Please enter manually.");
    } finally {
      setIsParsing(false);
    }
  };

  // Final Form Submission
  const onFormSubmit = async (formData) => {
    setIsSubmitting(true);
    try {
      // Assemble nested JSON according to backend models
      const payload = {
        patient_id: formData.patient_id,
        name: formData.name,
        age: parseInt(formData.age, 10),
        gender: formData.gender,
        admission_date: formData.admission_date || null,
        discharge_date: formData.discharge_date || null,
        primary_diagnosis: formData.primary_diagnosis,
        hospital_course_description: formData.hospital_course_description,
        treatment_summary: [],
        medications_at_discharge: formData.medications_at_discharge,
        discharge_instructions: formData.discharge_instructions,
        follow_up_appointments: [],
        responsible_physician: {
          name: formData.physician_name,
          contact: formData.physician_contact,
        },
        additional_notes: [],
        caretaker: {
          name: formData.caretaker_name,
          contact: formData.caretaker_contact,
          relationship: formData.caretaker_relationship,
        },
        reminders: formData.reminders,
        monitors: formData.monitors,
      };

      await createPatientRecord(payload);
      setSubmitSuccess(true);
      setTimeout(() => navigate("/patients"), 1000);
    } catch (err) {
      console.error("Patient creation failed:", err);
      alert("Failed to register patient. Please check your data.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="max-w-4xl mx-auto px-4 py-8 flex flex-col gap-6"
    >
      {/* Top Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.05, x: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => {
              if (viewMode === "form" || viewMode === "upload") {
                setViewMode("select");
              } else {
                navigate("/home");
              }
            }}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 shadow-sm transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </motion.button>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              Add New Patient
            </h1>
            <p className="text-xs text-slate-500">
              {viewMode === "select" && "Select registration mode"}
              {viewMode === "upload" && "Upload discharge summary photo"}
              {viewMode === "form" &&
                "Review, edit, and confirm patient protocol"}
            </p>
          </div>
        </div>
      </div>

      {/* ========================================================= */}
      {/* 1. INITIAL SELECTOR: MANUAL vs DISCHARGE SUMMARY UPLOAD   */}
      {/* ========================================================= */}
      {viewMode === "select" && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-5 pt-4"
        >
          {/* Option A: Add Manually */}
          <motion.button
            whileHover={{ y: -3, scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setViewMode("form")}
            className="flex flex-col items-start p-7 bg-white border border-slate-200 hover:border-indigo-400 rounded-2xl shadow-sm hover:shadow-md transition-all text-left group"
          >
            <div className="p-3.5 bg-indigo-50 text-indigo-600 rounded-xl group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-200 mb-4">
              <FileEdit className="w-7 h-7" />
            </div>
            <h2 className="text-xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
              Add Manually
            </h2>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Manually fill out demographics, discharge diagnosis, treatment
              medications, care reminders, and daily monitoring protocols.
            </p>
          </motion.button>

          {/* Option B: Upload Discharge Summary */}
          <motion.button
            whileHover={{ y: -3, scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setViewMode("upload")}
            className="flex flex-col items-start p-7 bg-white border border-slate-200 hover:border-indigo-400 rounded-2xl shadow-sm hover:shadow-md transition-all text-left group"
          >
            <div className="p-3.5 bg-emerald-50 text-emerald-600 rounded-xl group-hover:bg-emerald-600 group-hover:text-white transition-colors duration-200 mb-4">
              <UploadCloud className="w-7 h-7" />
            </div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
                Upload Discharge Summary
              </h2>
              <span className="flex items-center gap-1 text-[11px] font-semibold bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full">
                <Sparkles className="w-3 h-3" /> Auto-Extract
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-2 leading-relaxed">
              Upload a picture or scan of the physical discharge document. The
              system will automatically populate the registration fields for you
              to review.
            </p>
          </motion.button>
        </motion.div>
      )}

      {/* ========================================================= */}
      {/* 2. UPLOAD DISCHARGE SUMMARY FILE VIEW                     */}
      {/* ========================================================= */}
      {viewMode === "upload" && (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white border border-slate-200 rounded-2xl p-8 shadow-sm flex flex-col items-center justify-center text-center max-w-xl mx-auto w-full"
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*,.pdf"
            className="hidden"
          />

          <div className="p-5 bg-indigo-50 text-indigo-600 rounded-2xl mb-4">
            <UploadCloud className="w-10 h-10 animate-bounce" />
          </div>

          <h3 className="text-lg font-bold text-slate-800">
            Upload Hospital Discharge Paperwork
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mt-1 mb-6">
            Take a clear picture or upload a scanned image (PNG, JPG) of the
            patient's discharge summary.
          </p>

          {isParsing ? (
            <div className="flex flex-col items-center gap-2 py-4">
              <Loader2 className="w-7 h-7 text-indigo-600 animate-spin" />
              <span className="text-sm font-semibold text-slate-700">
                Extracting clinical information...
              </span>
              <span className="text-xs text-slate-400">
                Parsing diagnoses, meds, reminders, and monitoring criteria
              </span>
            </div>
          ) : (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => fileInputRef.current?.click()}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl shadow-sm hover:shadow-indigo-200 transition-all flex items-center gap-2 text-sm"
            >
              <FileText className="w-4 h-4" />
              Select File / Take Photo
            </motion.button>
          )}

          {selectedFile && !isParsing && (
            <p className="text-xs text-emerald-600 font-medium mt-4">
              Selected: {selectedFile.name}
            </p>
          )}
        </motion.div>
      )}

      {/* ========================================================= */}
      {/* 3. MULTI-SECTION COMPREHENSIVE FORM VIEW                  */}
      {/* ========================================================= */}
      {viewMode === "form" && (
        <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-8">
          {/* ========================================================= */}
          {/* SECTION 1: PATIENT DEMOGRAPHICS & CLINICAL SUMMARY        */}
          {/* ========================================================= */}
          <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-6">
            <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
              <User className="w-5 h-5 text-indigo-600" />
              <h2 className="text-lg font-bold text-slate-800">
                Section 1: Patient Information
              </h2>
            </div>

            {/* Row 1: ID, Name, Age, Gender */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Patient ID *
                </label>
                <input
                  type="text"
                  placeholder="e.g. PT-940"
                  {...register("patient_id", {
                    required: "Patient ID is required",
                  })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
                {errors.patient_id && (
                  <span className="text-[11px] text-red-500">
                    {errors.patient_id.message}
                  </span>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  placeholder="e.g. John Doe"
                  {...register("name", { required: "Name is required" })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
                {errors.name && (
                  <span className="text-[11px] text-red-500">
                    {errors.name.message}
                  </span>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Age *
                </label>
                <input
                  type="number"
                  placeholder="e.g. 58"
                  {...register("age", { required: "Age is required", min: 0 })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
                {errors.age && (
                  <span className="text-[11px] text-red-500">
                    {errors.age.message}
                  </span>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Gender *
                </label>
                <select
                  {...register("gender")}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none bg-white"
                >
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            {/* Row 2: Admission & Discharge Dates */}
            <div className="flex justify-between gap-4">
              <div className="flex-grow flex flex-col">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Admission Date
                </label>
                
                <input
                  type="date"
                  {...register("admission_date")}
                  className="px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
              <div className="flex-grow flex flex-col">
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Discharge Date
                </label>
                
                <input
                  type="date"
                  {...register("discharge_date")}
                  className=" px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
                
              </div>
            </div>

            {/* Row 3: Primary Diagnosis & Hospital Course */}
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Primary Diagnosis *
                </label>
                <input
                  type="text"
                  placeholder="e.g. Acute Coronary Syndrome with Stent"
                  {...register("primary_diagnosis", {
                    required: "Diagnosis is required",
                  })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
                {errors.primary_diagnosis && (
                  <span className="text-[11px] text-red-500">
                    {errors.primary_diagnosis.message}
                  </span>
                )}
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">
                  Hospital Course Description
                </label>
                <textarea
                  rows={3}
                  placeholder="Brief clinical course during admission..."
                  {...register("hospital_course_description")}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Row 4: Caretaker & Physician Info */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-2 border-t border-slate-100">
              {/* Caretaker Info */}
              <div className="space-y-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Primary Caretaker
                </span>
                <input
                  type="text"
                  placeholder="Caretaker Name"
                  {...register("caretaker_name", {
                    required: "Caretaker name is required",
                  })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
                <input
                  type="text"
                  placeholder="Caretaker Contact Number *"
                  {...register("caretaker_contact", {
                    required: "Caretaker contact is required",
                  })}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
                <input
                  type="text"
                  placeholder="Relationship (e.g. Spouse, Son)"
                  {...register("caretaker_relationship")}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              {/* Physician Info */}
              <div className="space-y-3">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Responsible Physician
                </span>
                <input
                  type="text"
                  placeholder="Doctor Name"
                  {...register("physician_name")}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
                <input
                  type="text"
                  placeholder="Physician Contact / Clinic"
                  {...register("physician_contact")}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>
            </div>

            {/* Dynamic Medications List */}
            <div className="pt-2 border-t border-slate-100 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Medications at Discharge
                </span>
                <button
                  type="button"
                  onClick={() =>
                    appendMed({
                      medication_name: "",
                      dosage: "",
                      frequency: "",
                      duration: "",
                    })
                  }
                  className="flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
                >
                  <Plus className="w-3.5 h-3.5" /> Add Med
                </button>
              </div>

              {medFields.map((field, idx) => (
                <div key={field.id} className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder="Medication name"
                    {...register(
                      `medications_at_discharge.${idx}.medication_name`
                    )}
                    className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                  <input
                    type="text"
                    placeholder="Dosage"
                    {...register(`medications_at_discharge.${idx}.dosage`)}
                    className="w-24 px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none"
                  />
                  <input
                    type="text"
                    placeholder="Frequency"
                    {...register(`medications_at_discharge.${idx}.frequency`)}
                    className="w-32 px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none"
                  />
                  {medFields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeMed(idx)}
                      className="p-2 text-slate-400 hover:text-red-500"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>

            {/* Dynamic Discharge Instructions */}
            <div className="pt-2 border-t border-slate-100 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  Discharge Instructions
                </span>
                <button
                  type="button"
                  onClick={() => appendInstruction({ instruction: "" })}
                  className="flex items-center gap-1 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
                >
                  <Plus className="w-3.5 h-3.5" /> Add Instruction
                </button>
              </div>

              {instructionFields.map((field, idx) => (
                <div key={field.id} className="flex items-center gap-2">
                  <input
                    type="text"
                    placeholder="e.g. Avoid lifting objects heavier than 10 lbs"
                    {...register(`discharge_instructions.${idx}.instruction`)}
                    className="flex-1 px-3 py-2 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                  {instructionFields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeInstruction(idx)}
                      className="p-2 text-slate-400 hover:text-red-500"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* ========================================================= */}
          {/* SECTION 2: REMINDERS CONFIGURATION                        */}
          {/* ========================================================= */}
          <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <Bell className="w-5 h-5 text-indigo-600" />
                <h2 className="text-lg font-bold text-slate-800">
                  Section 2: Reminders
                </h2>
              </div>
              <button
                type="button"
                onClick={() =>
                  appendReminder({
                    frequency: "daily",
                    time: "08:00",
                    content: "",
                  })
                }
                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 text-xs font-semibold rounded-lg transition-colors"
              >
                <Plus className="w-3.5 h-3.5" /> Add Reminder
              </button>
            </div>

            <div className="space-y-3">
              {reminderFields.map((field, idx) => (
                <div
                  key={field.id}
                  className="p-4 bg-slate-50/70 border border-slate-200 rounded-xl flex flex-col sm:flex-row items-start sm:items-center gap-3"
                >
                  <div className="grow flex flex-col"> 
                    <label className="block text-[11px] font-semibold text-slate-500 mb-1">
                      Frequency
                    </label>
                    <select
                      {...register(`reminders.${idx}.frequency`)}
                      className=" px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                    >
                      <option value="once">Once</option>
                      <option value="daily">Daily</option>
                    </select>
                  </div>

                  <div className="grow flex flex-col">
                    <label className="block text-[11px] font-semibold text-slate-500 mb-1">
                      Time
                    </label>
                    <input
                      type="time"
                      {...register(`reminders.${idx}.time`, { required: true })}
                      className="px-2.5 py-[3px] rounded-lg border border-slate-200 text-xs bg-white focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  <div className="grow-2 flex flex-col">
                    <label className="block text-[11px] font-semibold text-slate-500 mb-1">
                      Content / Instruction
                    </label>
                    <input
                      type="text"
                      placeholder="e.g. Take Aspirin 81mg with breakfast"
                      {...register(`reminders.${idx}.content`, {
                        required: true,
                      })}
                      className="px-3 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                    />
                  </div>

                  {reminderFields.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeReminder(idx)}
                      className="sm:mt-5 p-2 text-slate-400 hover:text-red-500"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* ========================================================= */}
          {/* SECTION 3: TELEMETRY MONITORS CONFIGURATION               */}
          {/* ========================================================= */}
          <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <Activity className="w-5 h-5 text-indigo-600" />
                <h2 className="text-lg font-bold text-slate-800">
                  Section 3: Monitors
                </h2>
              </div>
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
                className="flex items-center gap-1.5 px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-600 text-xs font-semibold rounded-lg transition-colors"
              >
                <Plus className="w-3.5 h-3.5" /> Add Monitor
              </button>
            </div>

            <div className="space-y-4">
              {monitorFields.map((field, idx) => (
                <div
                  key={field.id}
                  className="p-4 bg-slate-50/70 border border-slate-200 rounded-xl space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-indigo-600 uppercase tracking-wider">
                      Monitor #{idx + 1}
                    </span>
                    {monitorFields.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeMonitor(idx)}
                        className="text-slate-400 hover:text-red-500"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-[11px] font-semibold text-slate-500 mb-1">
                        Frequency
                      </label>
                      <select
                        {...register(`monitors.${idx}.frequency`)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                      >
                        <option value="once">Once</option>
                        <option value="daily">Daily</option>
                        <option value="per_week">Per Week</option>
                        <option value="per_month">Per Month</option>
                        <option value="per_year">Per Year</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-slate-500 mb-1">
                        Input Type
                      </label>
                      <select
                        {...register(`monitors.${idx}.input_type`)}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                      >
                        <option value="image">Image (Photo)</option>
                        <option value="video">Video</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-[11px] font-semibold text-slate-500 mb-1">
                        Check-in Time
                      </label>
                      <input
                        type="time"
                        {...register(`monitors.${idx}.time`, {
                          required: true,
                        })}
                        className="w-full px-2.5 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                      />
                    </div>
                  </div>

                  <div className="space-y-2 pt-1">
                    <input
                      type="text"
                      placeholder="Instructions for Patient (e.g. Capture clear photo of right groin surgical incision)"
                      {...register(`monitors.${idx}.instructions`, {
                        required: true,
                      })}
                      className="w-full px-3 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                    />

                    <input
                      type="text"
                      placeholder="Things to Evaluate (e.g. Check for erythema, dehiscence, or spreading hematoma)"
                      {...register(`monitors.${idx}.things_to_evaluate`, {
                        required: true,
                      })}
                      className="w-full px-3 py-1.5 rounded-lg border border-slate-200 text-xs bg-white focus:outline-none"
                    />

                    <input
                      type="text"
                      placeholder="Trigger Alert If (e.g. Visible hematoma > 2cm or active bleeding)"
                      {...register(`monitors.${idx}.trigger_alert_if`, {
                        required: true,
                      })}
                      className="w-full px-3 py-1.5 rounded-lg border border-red-200 text-xs bg-white focus:outline-none placeholder-red-300 text-red-900"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Form Actions / Submit */}
          <div className="flex items-center justify-end gap-4 pt-4">
            <button
              type="button"
              onClick={() => setViewMode("select")}
              className="px-5 py-2.5 border border-slate-200 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>

            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isSubmitting || submitSuccess}
              className={`flex items-center gap-2 px-6 py-3 text-white font-semibold text-sm rounded-xl shadow-md transition-all ${
                submitSuccess
                  ? "bg-emerald-600"
                  : "bg-indigo-600 hover:bg-indigo-700 hover:shadow-indigo-200"
              }`}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Registering Patient...
                </>
              ) : submitSuccess ? (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Patient Created!
                </>
              ) : (
                "Create Patient & Schedule Protocols"
              )}
            </motion.button>
          </div>
        </form>
      )}
    </motion.div>
  );
}
