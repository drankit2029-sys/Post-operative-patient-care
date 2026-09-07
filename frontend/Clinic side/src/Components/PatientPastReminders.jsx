import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Bell,
  Clock,
  CheckCircle2,
  XCircle,
  Calendar,
  ChevronRight,
  History,
  AlertCircle,
  Sparkles,
} from "lucide-react";

// Separate API Stub for fetching reminders and past events
export async function fetchPatientRemindersData(patientId) {
  // TODO: Replace with Axios call (e.g., const res = await axios.get(`http://localhost:8000/api/v1/patients/${patientId}/reminders`); return res.data;)
  await new Promise((resolve) => setTimeout(resolve, 200));

  return {
    patient_id: patientId || "PT-904",
    patient_name: "Eleanor Vance",
    reminders: [
      {
        id: 101,
        frequency: "daily",
        time: "08:00",
        content: "Take Aspirin 81mg and Ticagrelor 90mg with breakfast.",
        created_at: "2026-08-30T11:00:00Z",
      },
      {
        id: 102,
        frequency: "daily",
        time: "20:00",
        content: "Take Ticagrelor 90mg and Atorvastatin 80mg at bedtime.",
        created_at: "2026-08-30T11:00:00Z",
      },
      {
        id: 103,
        frequency: "daily",
        time: "09:00",
        content: "Take Metoprolol Succinate 50mg with morning glass of water.",
        created_at: "2026-08-30T11:00:00Z",
      },
      {
        id: 104,
        frequency: "once",
        time: "14:00",
        content: "Prescription refill delivery arrival verification.",
        created_at: "2026-09-02T09:30:00Z",
      },
      {
        id: 105,
        frequency: "daily",
        time: "12:30",
        content: "Record post-lunch resting blood pressure and heart rate.",
        created_at: "2026-09-03T15:00:00Z",
      },
    ],
    past_events: [
      {
        id: 301,
        reminder_id: 101,
        content: "Morning antiplatelet dose confirmation.",
        resolved_or_not: true,
        created_at: "2026-09-07T08:12:00Z",
      },
      {
        id: 302,
        reminder_id: 102,
        content: "Evening Ticagrelor and statin dose confirmation.",
        resolved_or_not: true,
        created_at: "2026-09-06T20:18:00Z",
      },
      {
        id: 303,
        reminder_id: 105,
        content: "Post-lunch vitals reading input prompt.",
        resolved_or_not: false,
        created_at: "2026-09-06T13:15:00Z",
      },
      {
        id: 304,
        reminder_id: 101,
        content: "Morning antiplatelet dose confirmation.",
        resolved_or_not: true,
        created_at: "2026-09-06T08:05:00Z",
      },
    ],
  };
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

export default function PatientPastReminders() {
  const { id } = useParams();
  const navigate = useAnimatedNavigate();

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const result = await fetchPatientRemindersData(id);
        if (isMounted) setData(result);
      } catch (err) {
        console.error("Failed to load reminders:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 flex flex-col items-center justify-center text-slate-400 gap-3">
        <Clock className="w-8 h-8 animate-spin text-indigo-600" />
        <span className="text-sm font-medium">
          Loading reminders schedule...
        </span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-2" />
        <h2 className="text-lg font-bold text-slate-800">
          Reminders Not Found
        </h2>
        <button
          onClick={() => navigate(`/patients/${id}`)}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white text-xs font-semibold rounded-xl"
        >
          Return to Patient Details
        </button>
      </div>
    );
  }

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
            onClick={() => navigate(`/patients/${id}`)}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 shadow-sm transition-colors"
            title="Back to Patient Details"
          >
            <ArrowLeft className="w-5 h-5" />
          </motion.button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">
                All Scheduled Reminders
              </h1>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                {data.patient_id}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Active medication and care regimens for{" "}
              <span className="font-semibold text-slate-700">
                {data.patient_name}
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Section 1: All Active Configured Reminders */}
      <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <Bell className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800">
                Active Regimen Reminders
              </h2>
              <p className="text-xs text-slate-400">
                Click any reminder card to view or adjust trigger configurations
              </p>
            </div>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-lg">
            {data.reminders.length} Configured
          </span>
        </div>

        <div className="space-y-3">
          {data.reminders.map((reminder) => (
            <motion.div
              key={reminder.id}
              whileHover={{ y: -2, scale: 1.005 }}
              whileTap={{ scale: 0.985 }}
              onClick={() =>
                navigate(`/patients/${id}/reminders/${reminder.id}`)
              }
              className="p-4 bg-slate-50/70 hover:bg-white border border-slate-200 hover:border-indigo-300 rounded-xl flex items-center justify-between cursor-pointer transition-all shadow-2xs group"
            >
              <div className="flex items-center gap-4">
                <div className="flex flex-col items-center justify-center p-2.5 bg-indigo-50 rounded-xl border border-indigo-100 min-w-[68px]">
                  <span className="text-xs font-mono font-bold text-indigo-700 flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {reminder.time}
                  </span>
                  <span className="text-[10px] font-semibold text-indigo-500 uppercase mt-0.5">
                    {reminder.frequency}
                  </span>
                </div>

                <div>
                  <h3 className="text-sm font-bold text-slate-800 group-hover:text-indigo-600 transition-colors">
                    {reminder.content}
                  </h3>
                  <span className="text-[11px] text-slate-400">
                    Reminder ID: #{reminder.id}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2 text-slate-400 group-hover:text-indigo-600">
                <span className="text-xs font-semibold hidden sm:inline">
                  Details
                </span>
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Section 2: Past Reminder Event History */}
      <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
          <div className="p-2 bg-slate-100 text-slate-600 rounded-xl">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-800">
              Past Reminder Event Log
            </h2>
            <p className="text-xs text-slate-400">
              Historical delivery responses and patient compliance
            </p>
          </div>
        </div>

        {data.past_events.length === 0 ? (
          <p className="text-xs text-slate-400 py-3">
            No past reminder events logged yet.
          </p>
        ) : (
          <div className="space-y-2.5">
            {data.past_events.map((event) => (
              <div
                key={event.id}
                className="p-3.5 bg-slate-50/60 rounded-xl border border-slate-200 flex items-center justify-between gap-3 text-xs"
              >
                <div className="flex items-center gap-3">
                  {event.resolved_or_not ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-500 shrink-0" />
                  ) : (
                    <XCircle className="w-5 h-5 text-amber-500 shrink-0" />
                  )}
                  <div>
                    <span className="font-semibold text-slate-800 block">
                      {event.content}
                    </span>
                    <span className="text-[11px] text-slate-400">
                      Target Reminder: #{event.reminder_id || "N/A"} •{" "}
                      {new Date(event.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <span
                  className={`text-[11px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider ${
                    event.resolved_or_not
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-amber-100 text-amber-800"
                  }`}
                >
                  {event.resolved_or_not ? "Acknowledged" : "Unresolved"}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </motion.div>
  );
}
