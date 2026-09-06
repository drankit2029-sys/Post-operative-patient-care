import { useState, useEffect, useMemo, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  ArrowLeft,
  AlertTriangle,
  Phone,
  Calendar,
  Stethoscope,
  ChevronRight,
  User,
  X,
  Clock,
  ShieldCheck,
} from "lucide-react";

// --- SEPARATE FETCH FUNCTION ---
// Keep fetching logic isolated here. When your backend is ready, replace with:
// const { data } = await axios.get('/api/patients'); return data;
export async function fetchPatientsList() {
  // Mock API network latency
  await new Promise((resolve) => setTimeout(resolve, 100));

  const mockPatients = [
    {
      patient_id: "PT-904",
      name: "Eleanor Vance",
      age: 68,
      gender: "Female",
      caretaker_no: "+1 (555) 234-5678",
      date_of_discharge: "2026-08-30",
      created_at: "2026-08-30T10:15:00Z",
      final_diagnosis:
        "Acute Coronary Syndrome, Post-PCI with drug-eluting stent",
      recent_alert: {
        id: "ALT-101",
        patientId: "PT-904",
        patientName: "Eleanor Vance",
        caretakerContact: "+1 (555) 234-5678",
        content:
          "Critical drop in SpO2: 84% at resting state. Requires immediate assessment.",
        priority: "critical",
        timestamp: "4m ago",
      },
    },
    {
      patient_id: "PT-882",
      name: "Marcus Holloway",
      age: 54,
      gender: "Male",
      caretaker_no: "+1 (555) 876-5432",
      date_of_discharge: "2026-08-28",
      created_at: "2026-08-28T14:40:00Z",
      final_diagnosis:
        "Hypertensive Emergency resolved, Essential Hypertension Stage II",
      recent_alert: {
        id: "ALT-102",
        patientId: "PT-882",
        patientName: "Marcus Holloway",
        caretakerContact: "+1 (555) 876-5432",
        content: "Acute systolic blood pressure spike detected: 178/95 mmHg.",
        priority: "critical",
        timestamp: "19m ago",
      },
    },
    {
      patient_id: "PT-765",
      name: "Sophia Reyes",
      age: 42,
      gender: "Female",
      caretaker_no: "+1 (555) 345-6789",
      date_of_discharge: "2026-08-24",
      created_at: "2026-08-24T09:00:00Z",
      final_diagnosis: "Supraventricular Tachycardia (Ablated), Hypokalemia",
      recent_alert: {
        id: "ALT-103",
        patientId: "PT-765",
        patientName: "Sophia Reyes",
        caretakerContact: "+1 (555) 345-6789",
        content: "Missed scheduled evening medication: Metoprolol 50mg.",
        priority: "high",
        timestamp: "45m ago",
      },
    },
    {
      patient_id: "PT-630",
      name: "Arthur Pendelton",
      age: 73,
      gender: "Male",
      caretaker_no: "+1 (555) 987-6543",
      date_of_discharge: "2026-08-20",
      created_at: "2026-08-20T11:20:00Z",
      final_diagnosis:
        "Type 2 Diabetes Mellitus with hyperosmolar state, Diabetic Nephropathy",
      recent_alert: {
        id: "ALT-104",
        patientId: "PT-630",
        patientName: "Arthur Pendelton",
        caretakerContact: "+1 (555) 987-6543",
        content:
          "Continuous glucose monitor indicates persistent hypoglycemia (<60 mg/dL).",
        priority: "critical",
        timestamp: "1h ago",
      },
    },
    {
      patient_id: "PT-512",
      name: "Amara Chen",
      age: 36,
      gender: "Female",
      caretaker_no: "+1 (555) 432-1098",
      date_of_discharge: "2026-08-15",
      created_at: "2026-08-15T08:30:00Z",
      final_diagnosis:
        "Community-Acquired Pneumonia (Resolved), Asthma Exacerbation",
      recent_alert: null, // No active alerts
    },
    {
      patient_id: "PT-401",
      name: "James Wilson",
      age: 61,
      gender: "Male",
      caretaker_no: "+1 (555) 654-3210",
      date_of_discharge: "2026-08-10",
      created_at: "2026-08-10T16:05:00Z",
      final_diagnosis:
        "Subcapital Femur Fracture Post-ORIF, Post-op Rehabilitation",
      recent_alert: {
        id: "ALT-106",
        patientId: "PT-401",
        patientName: "James Wilson",
        caretakerContact: "+1 (555) 654-3210",
        content:
          "Fall detection sensor telemetry event recorded - checked and stable.",
        priority: "low",
        timestamp: "3h ago",
      },
    },
  ];

  return mockPatients;
}

// Custom animated navigate to complete tap animations cleanly
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

// Animation Variants
const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.3, ease: [0.25, 1, 0.5, 1] },
  },
  exit: { opacity: 0, y: -10, transition: { duration: 0.18 } },
};

const listContainerVariants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: { staggerChildren: 0.05, delayChildren: 0.05 },
  },
};

const cardVariants = {
  initial: { opacity: 0, y: 14 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 400, damping: 28 },
  },
};

export default function Patients() {
  const navigate = useAnimatedNavigate();
  const [patients, setPatients] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const data = await fetchPatientsList();
        // Arrange by timestamp of creation: most recent ones at top
        const sorted = [...data].sort(
          (a, b) =>
            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
        setPatients(sorted);
      } catch (err) {
        console.error("Failed to fetch patients:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Filter based on patient name or patient_id
  const filteredPatients = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return patients;

    return patients.filter((patient) => {
      const nameMatch = patient.name.toLowerCase().includes(q);
      const idMatch = patient.patient_id.toLowerCase().includes(q);
      return nameMatch || idMatch;
    });
  }, [patients, searchQuery]);

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="max-w-4xl mx-auto px-4 py-8 flex flex-col gap-6"
    >
      {/* Header & Search Bar */}
      <header className="flex flex-col gap-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <motion.button
              whileHover={{ scale: 1.08, x: -2 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: "spring", stiffness: 500, damping: 20 }}
              onClick={() => navigate("/home")}
              className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 shadow-sm transition-colors select-none active:outline-none"
              title="Back to Home"
            >
              <ArrowLeft className="w-5 h-5" />
            </motion.button>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-2xl font-bold text-slate-900">
                  Patients Registry
                </h1>
                <span className="text-xs font-bold px-2 py-0.5 rounded-full bg-indigo-100 text-indigo-700">
                  {patients.length} Total
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Sorted by newest registered patients
              </p>
            </div>
          </div>
        </div>

        {/* Search Input Box */}
        <div className="relative">
          <Search className="w-5 h-5 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by patient name or ID (e.g., 'Eleanor' or 'PT-904')..."
            className="w-full pl-11 pr-10 py-3 rounded-xl border border-slate-200 bg-white text-slate-800 placeholder-slate-400 shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all text-sm"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 p-1 text-slate-400 hover:text-slate-600 rounded-md transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
      </header>

      {/* Patient Cards List */}
      <section className="flex flex-col gap-4">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 text-slate-400 gap-2">
            <Clock className="w-6 h-6 animate-spin text-indigo-500" />
            <span className="text-sm">Loading patient records...</span>
          </div>
        ) : filteredPatients.length === 0 ? (
          <div className="text-center py-16 bg-white border border-slate-200 rounded-2xl p-6">
            <User className="w-10 h-10 text-slate-300 mx-auto mb-2" />
            <p className="text-base font-semibold text-slate-700">
              No patients matched your query
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Check the spelling or try searching for another identifier.
            </p>
          </div>
        ) : (
          <motion.div
            variants={listContainerVariants}
            initial="initial"
            animate="animate"
            className="space-y-4"
          >
            <AnimatePresence>
              {filteredPatients.map((patient) => {
                const recentAlert = patient.recent_alert;
                const isCriticalAlert =
                  recentAlert &&
                  recentAlert.priority?.toLowerCase() === "critical";

                return (
                  <motion.div
                    key={patient.patient_id}
                    variants={cardVariants}
                    layout
                    whileHover={{ y: -3, scale: 1.006 }}
                    whileTap={{ scale: 0.985 }}
                    transition={{ type: "spring", stiffness: 450, damping: 24 }}
                    onClick={() => navigate(`/patients/${patient.patient_id}`)}
                    className="p-5 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:border-indigo-300 cursor-pointer transition-all duration-200 select-none group"
                  >
                    {/* Top Row: Basic Info & Primary Identifiers */}
                    <div className="flex items-start justify-between gap-3 pb-3 border-b border-slate-100">
                      <div>
                        <div className="flex items-center gap-2.5 flex-wrap">
                          <h2 className="text-lg font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                            {patient.name}
                          </h2>
                          <span className="text-xs font-mono font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                            {patient.patient_id}
                          </span>
                          <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                            {patient.age} yrs • {patient.gender}
                          </span>
                        </div>
                      </div>

                      <div className="flex items-center text-slate-400 group-hover:text-indigo-600 transition-colors shrink-0">
                        <span className="text-xs font-medium hidden sm:inline mr-1">
                          View Details
                        </span>
                        <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                      </div>
                    </div>

                    {/* Middle Section: Medical & Operational Details */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 py-3 text-xs text-slate-600">
                      {/* Diagnosis */}
                      <div className="flex items-start gap-2">
                        <Stethoscope className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                        <div>
                          <span className="text-slate-400 font-medium block">
                            Final Diagnosis:
                          </span>
                          <span className="font-semibold text-slate-800">
                            {patient.final_diagnosis}
                          </span>
                        </div>
                      </div>

                      {/* Caretaker & Discharge Date */}
                      <div className="space-y-1.5">
                        <div className="flex items-center gap-2">
                          <Phone className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span>
                            Caretaker:{" "}
                            <span className="font-medium text-slate-800">
                              {patient.caretaker_no}
                            </span>
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Calendar className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span>
                            Discharged:{" "}
                            <span className="font-medium text-slate-800">
                              {patient.date_of_discharge}
                            </span>
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Bottom Section: Recent Alert Area */}
                    <div className="pt-3 border-t border-slate-100/90">
                      {recentAlert ? (
                        <div
                          className={`p-3 rounded-xl border flex flex-col gap-1.5 ${
                            isCriticalAlert
                              ? "bg-red-50/80 border-red-200"
                              : "bg-amber-50/70 border-amber-200"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-1.5">
                              <AlertTriangle
                                className={`w-3.5 h-3.5 shrink-0 ${
                                  isCriticalAlert
                                    ? "text-red-600 animate-pulse"
                                    : "text-amber-600"
                                }`}
                              />
                              <span
                                className={`text-[11px] font-bold uppercase tracking-wider ${
                                  isCriticalAlert
                                    ? "text-red-700"
                                    : "text-amber-700"
                                }`}
                              >
                                Most Recent Alert ({recentAlert.priority})
                              </span>
                            </div>
                            <span className="text-[11px] text-slate-400">
                              {recentAlert.timestamp}
                            </span>
                          </div>

                          {/* Content colored red if critical */}
                          <p
                            className={`text-xs ${
                              isCriticalAlert
                                ? "text-red-600 font-semibold"
                                : "text-slate-700 font-normal"
                            }`}
                          >
                            {recentAlert.content}
                          </p>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 text-xs text-emerald-600 bg-emerald-50/70 px-3 py-2 rounded-xl border border-emerald-100">
                          <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                          <span className="font-medium">
                            No active alerts recorded
                          </span>
                        </div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </AnimatePresence>
          </motion.div>
        )}
      </section>
    </motion.div>
  );
}
