import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Activity,
  Clock,
  Camera,
  Video,
  ShieldAlert,
  ChevronRight,
  History,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
} from "lucide-react";

// Separate API Stub for fetching monitors and past events
export async function fetchPatientMonitorsData(patientId) {
  // TODO: Replace with Axios call (e.g., const res = await axios.get(`http://localhost:8000/api/v1/patients/${patientId}/monitors`); return res.data;)
  await new Promise((resolve) => setTimeout(resolve, 200));

  return {
    patient_id: patientId || "PT-904",
    patient_name: "Eleanor Vance",
    monitors: [
      {
        id: 201,
        frequency: "daily",
        input_type: "image",
        time: "10:00",
        instructions:
          "Take a well-lit photo of the right femoral access puncture site.",
        things_to_evaluate:
          "Check for expanding hematoma, active bleeding, spreading erythema, or purulence.",
        trigger_alert_if:
          "Erythema exceeds 2cm from puncture site, swelling palpated, or visible hematoma enlargement.",
      },
      {
        id: 202,
        frequency: "daily",
        input_type: "image",
        time: "08:30",
        instructions:
          "Photograph the LCD screen of your automated blood pressure monitor.",
        things_to_evaluate:
          "Systolic blood pressure, diastolic blood pressure, and pulse rate.",
        trigger_alert_if:
          "Systolic BP > 160 or < 90 mmHg, or Heart Rate < 50 bpm.",
      },
      {
        id: 203,
        frequency: "daily",
        input_type: "video",
        time: "18:00",
        instructions:
          "Record a 10-second video of your normal respiratory pattern while seated resting.",
        things_to_evaluate:
          "Accessory muscle use, tachypnea, or shallow breathing.",
        trigger_alert_if:
          "Visible respiratory distress or respiratory rate exceeding 24 breaths/min.",
      },
      {
        id: 204,
        frequency: "per_week",
        input_type: "image",
        time: "09:00",
        instructions:
          "Photograph bilateral ankles to assess for dependent fluid retention.",
        things_to_evaluate: "Pitting pretibial edema.",
        trigger_alert_if: "New or progressive pitting edema noticed.",
      },
    ],
    past_events: [
      {
        id: 401,
        monitor_id: 201,
        input_given: "/uploads/PT-904/groin_day6.jpg",
        remark:
          "Puncture site clean, minimal residual bruising, no signs of infection or pseudoaneurysm.",
        alert_triggered_or_not: false,
        created_at: "2026-09-07T10:14:00Z",
      },
      {
        id: 402,
        monitor_id: 202,
        input_given: "/uploads/PT-904/bp_screen_sept06.jpg",
        remark:
          "Blood pressure readout 172/96 mmHg triggered automated threshold escalation.",
        alert_triggered_or_not: true,
        created_at: "2026-09-06T08:34:00Z",
      },
      {
        id: 403,
        monitor_id: 203,
        input_given: "/uploads/PT-904/resp_pattern.mp4",
        remark:
          "Normal resting respiratory rate (16 bpm) without suprasternal retractions.",
        alert_triggered_or_not: false,
        created_at: "2026-09-05T18:02:00Z",
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

export default function PatientMonitors() {
  const { id } = useParams();
  const navigate = useAnimatedNavigate();

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const result = await fetchPatientMonitorsData(id);
        if (isMounted) setData(result);
      } catch (err) {
        console.error("Failed to load monitors:", err);
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
          Loading telemetry protocols...
        </span>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-2" />
        <h2 className="text-lg font-bold text-slate-800">Monitors Not Found</h2>
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
                All Telemetry Monitors
              </h1>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                {data.patient_id}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Active imaging and video surveillance protocols for{" "}
              <span className="font-semibold text-slate-700">
                {data.patient_name}
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Section 1: All Active Configured Monitors */}
      <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800">
                Telemetry Surveillance Protocols
              </h2>
              <p className="text-xs text-slate-400">
                Click any monitor to inspect individual event thresholds and
                evaluations
              </p>
            </div>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-lg">
            {data.monitors.length} Active Protocols
          </span>
        </div>

        <div className="space-y-4">
          {data.monitors.map((monitor) => (
            <motion.div
              key={monitor.id}
              whileHover={{ y: -2, scale: 1.005 }}
              whileTap={{ scale: 0.985 }}
              onClick={() => navigate(`/patients/${id}/monitors/${monitor.id}`)}
              className="p-5 bg-slate-50/70 hover:bg-white border border-slate-200 hover:border-indigo-300 rounded-xl cursor-pointer transition-all shadow-2xs group flex flex-col gap-3"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="p-2 rounded-lg bg-indigo-50 text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                    {monitor.input_type === "video" ? (
                      <Video className="w-4 h-4" />
                    ) : (
                      <Camera className="w-4 h-4" />
                    )}
                  </span>
                  <div>
                    <h3 className="text-sm font-bold text-slate-900 group-hover:text-indigo-600 transition-colors">
                      {monitor.instructions}
                    </h3>
                    <span className="text-[11px] text-slate-400">
                      Protocol ID: #{monitor.id}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs font-mono font-semibold px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700">
                    {monitor.time} • {monitor.frequency}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 group-hover:text-indigo-600 transition-all" />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-2.5 text-xs pt-2 border-t border-slate-100">
                <div className="p-2.5 bg-white rounded-lg border border-slate-200/80">
                  <span className="font-semibold text-slate-400 block text-[10px] uppercase">
                    Things to Evaluate
                  </span>
                  <p className="text-slate-700 mt-0.5">
                    {monitor.things_to_evaluate}
                  </p>
                </div>

                <div className="p-2.5 bg-red-50/70 rounded-lg border border-red-200/80 text-red-900 flex items-start gap-1.5">
                  <ShieldAlert className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                  <div>
                    <span className="font-bold text-red-600 block text-[10px] uppercase">
                      Alert Trigger Threshold
                    </span>
                    <p className="font-medium text-xs mt-0.5">
                      {monitor.trigger_alert_if}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Section 2: Past Monitor Event Log */}
      <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center gap-2.5 pb-3 border-b border-slate-100">
          <div className="p-2 bg-slate-100 text-slate-600 rounded-xl">
            <History className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-800">
              Telemetry Ingestion Log
            </h2>
            <p className="text-xs text-slate-400">
              Uploaded check-ins and clinical algorithmic feedback
            </p>
          </div>
        </div>

        {data.past_events.length === 0 ? (
          <p className="text-xs text-slate-400 py-3">
            No monitoring files uploaded yet.
          </p>
        ) : (
          <div className="space-y-3">
            {data.past_events.map((event) => (
              <div
                key={event.id}
                className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs ${
                  event.alert_triggered_or_not
                    ? "bg-red-50/80 border-red-200"
                    : "bg-slate-50/70 border-slate-200"
                }`}
              >
                <div className="flex items-start gap-3">
                  {event.alert_triggered_or_not ? (
                    <AlertTriangle className="w-5 h-5 text-red-600 shrink-0 animate-pulse mt-0.5" />
                  ) : (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
                  )}

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-slate-900">
                        {event.alert_triggered_or_not
                          ? "Alert Triggered"
                          : "Telemetry Evaluated Normal"}
                      </span>
                      <span className="text-slate-400 text-[11px] font-mono">
                        ({event.input_given.split("/").pop()})
                      </span>
                    </div>

                    <p
                      className={`mt-1 ${
                        event.alert_triggered_or_not
                          ? "text-red-950 font-medium"
                          : "text-slate-600"
                      }`}
                    >
                      {event.remark}
                    </p>

                    <span className="text-[10px] text-slate-400 mt-1 block">
                      Target Monitor: #{event.monitor_id || "N/A"} •{" "}
                      {new Date(event.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <span
                  className={`self-start sm:self-auto text-[11px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider shrink-0 ${
                    event.alert_triggered_or_not
                      ? "bg-red-600 text-white shadow-2xs"
                      : "bg-emerald-100 text-emerald-800"
                  }`}
                >
                  {event.alert_triggered_or_not ? "Critical Event" : "Stable"}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </motion.div>
  );
}
