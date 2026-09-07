import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Bell,
  Clock,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  History,
  ShieldCheck,
  AlertCircle,
} from "lucide-react";

// API Stub: Fetch individual reminder, its specific past events, and linked alerts
export async function fetchReminderDetail(patientId, reminderId) {
  // TODO: Replace with Axios call
  // const res = await axios.get(`http://localhost:8000/api/v1/patients/${patientId}/reminders/${reminderId}`);
  // return res.data;
  await new Promise((resolve) => setTimeout(resolve, 200));

  return {
    reminder: {
      id: Number(reminderId),
      patient_id: patientId || "PT-904",
      patient_name: "Eleanor Vance",
      frequency: "daily",
      time: "08:00",
      content: "Take Aspirin 81mg and Ticagrelor 90mg with breakfast.",
      created_at: "2026-08-30T11:00:00Z",
    },
    // Alerts triggered specifically by non-compliance or issues with this reminder
    alerts: [
      {
        id: "ALT-103",
        patient_id: patientId || "PT-904",
        reminder_id: Number(reminderId),
        content:
          "Missed scheduled morning dose: Aspirin 81mg and Ticagrelor 90mg.",
        priority: "high",
        timestamp: "45m ago",
      },
    ],
    // Event telemetry filtered specifically for this reminder ID
    past_events: [
      {
        id: 301,
        reminder_id: Number(reminderId),
        content: "Morning antiplatelet dose confirmation.",
        resolved_or_not: true,
        created_at: "2026-09-07T08:12:00Z",
      },
      {
        id: 304,
        reminder_id: Number(reminderId),
        content: "Morning antiplatelet dose confirmation.",
        resolved_or_not: true,
        created_at: "2026-09-06T08:05:00Z",
      },
      {
        id: 308,
        reminder_id: Number(reminderId),
        content:
          "Morning antiplatelet dose confirmation - unacknowledged after 60 mins.",
        resolved_or_not: false,
        created_at: "2026-09-05T09:00:00Z",
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

export default function PatientReminder() {
  const { id, reminder_id } = useParams();
  const navigate = useAnimatedNavigate();

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const result = await fetchReminderDetail(id, reminder_id);
        if (isMounted) setData(result);
      } catch (err) {
        console.error("Failed to load reminder details:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [id, reminder_id]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 flex flex-col items-center justify-center text-slate-400 gap-3">
        <Clock className="w-8 h-8 animate-spin text-indigo-600" />
        <span className="text-sm font-medium">Loading reminder profile...</span>
      </div>
    );
  }

  if (!data?.reminder) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-2" />
        <h2 className="text-lg font-bold text-slate-800">Reminder Not Found</h2>
        <button
          onClick={() => navigate(`/patients/${id}/reminders`)}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white text-xs font-semibold rounded-xl"
        >
          Back to Reminders List
        </button>
      </div>
    );
  }

  const { reminder, alerts, past_events } = data;

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="max-w-4xl mx-auto px-4 py-8 flex flex-col gap-6"
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200">
        <div className="flex items-center gap-3">
          <motion.button
            whileHover={{ scale: 1.05, x: -2 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => navigate(`/patients/${id}/reminders`)}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 shadow-sm transition-colors"
            title="Back to Reminders"
          >
            <ArrowLeft className="w-5 h-5" />
          </motion.button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">
                Reminder #{reminder.id}
              </h1>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                {reminder.patient_id}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Assigned to{" "}
              <span className="font-semibold text-slate-700">
                {reminder.patient_name}
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Section 1: Reminder Core Details */}
      <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <Bell className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-slate-800">
              Regimen Specification
            </h2>
          </div>
          <span className="text-xs font-mono font-bold px-3 py-1 bg-indigo-50 text-indigo-700 rounded-lg flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            {reminder.time} ({reminder.frequency})
          </span>
        </div>

        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80">
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
            Prompt / Notification Message
          </span>
          <p className="text-base font-semibold text-slate-800">
            {reminder.content}
          </p>
        </div>

        <div className="text-[11px] text-slate-400">
          Created: {new Date(reminder.created_at).toLocaleDateString()}
        </div>
      </section>

      {/* Section 2: Alerts Specific to this Reminder */}
      <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-amber-50 text-amber-600 rounded-xl">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800">
                Linked Regimen Alerts
              </h2>
              <p className="text-xs text-slate-400">
                Alerts generated directly by missed intake or delayed response
              </p>
            </div>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-amber-50 text-amber-700">
            {alerts.length} Active
          </span>
        </div>

        {alerts.length === 0 ? (
          <div className="flex items-center gap-2 text-xs text-emerald-600 bg-emerald-50/70 px-4 py-3 rounded-xl border border-emerald-100">
            <ShieldCheck className="w-4 h-4 shrink-0" />
            <span>No unresolved alerts logged for this reminder.</span>
          </div>
        ) : (
          <div className="space-y-3">
            {alerts.map((alert) => {
              const isCritical = alert.priority.toLowerCase() === "critical";
              return (
                <div
                  key={alert.id}
                  className={`p-4 rounded-xl border ${
                    isCritical
                      ? "bg-red-50/90 border-red-300"
                      : "bg-amber-50/70 border-amber-200"
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
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
                    <span className="text-xs text-slate-400">
                      {alert.timestamp}
                    </span>
                  </div>
                  <p
                    className={`text-xs font-medium ${
                      isCritical ? "text-red-950" : "text-slate-800"
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

      {/* Section 3: Ingestion History for this specific reminder */}
      <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
          <div className="p-2 bg-slate-100 text-slate-600 rounded-xl">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-800">
              Compliance & Dispatch History
            </h2>
            <p className="text-xs text-slate-400">
              Past trigger instances and acknowledgments for Reminder #
              {reminder.id}
            </p>
          </div>
        </div>

        {past_events.length === 0 ? (
          <p className="text-xs text-slate-400 py-3">
            No event logs recorded for this reminder.
          </p>
        ) : (
          <div className="space-y-2.5">
            {past_events.map((event) => (
              <div
                key={event.id}
                className="p-3.5 bg-slate-50/60 rounded-xl border border-slate-200 flex items-center justify-between text-xs"
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
                      {new Date(event.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <span
                  className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase tracking-wider ${
                    event.resolved_or_not
                      ? "bg-emerald-100 text-emerald-800"
                      : "bg-amber-100 text-amber-800"
                  }`}
                >
                  {event.resolved_or_not ? "Confirmed" : "Unacknowledged"}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </motion.div>
  );
}
