import { useState, useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  ArrowLeft,
  Activity,
  Camera,
  Video,
  Clock,
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  History,
  ShieldCheck,
  AlertCircle,
  FileCheck,
} from "lucide-react";
import axios from "axios";
// API Stub: Fetch individual monitor protocol, its specific past events, and linked alerts
export async function fetchMonitorDetail(patientId, monitorId) {
  // TODO: Replace with Axios call
  const res = await axios.get(
    `/api/api/v1/patients/${patientId}/monitors/${monitorId}`
  );
  return res.data;
  
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

export default function PatientMonitor() {
  const { id, monitor_id } = useParams();
  const navigate = useAnimatedNavigate();

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);

  useEffect(() => {
    let isMounted = true;
    async function loadData() {
      setLoading(true);
      try {
        const result = await fetchMonitorDetail(id, monitor_id);
        if (isMounted) setData(result);
      } catch (err) {
        console.error("Failed to load monitor details:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadData();
    return () => {
      isMounted = false;
    };
  }, [id, monitor_id]);

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 flex flex-col items-center justify-center text-slate-400 gap-3">
        <Clock className="w-8 h-8 animate-spin text-indigo-600" />
        <span className="text-sm font-medium">Loading protocol details...</span>
      </div>
    );
  }

  if (!data?.monitor) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20 text-center">
        <AlertCircle className="w-10 h-10 text-red-500 mx-auto mb-2" />
        <h2 className="text-lg font-bold text-slate-800">Monitor Not Found</h2>
        <button
          onClick={() => navigate(`/patients/${id}/monitors`)}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white text-xs font-semibold rounded-xl"
        >
          Back to Monitors List
        </button>
      </div>
    );
  }

  const { monitor, alerts, past_events } = data;

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
            onClick={() => navigate(`/patients/${id}/monitors`)}
            className="p-2.5 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 shadow-sm transition-colors"
            title="Back to Monitors"
          >
            <ArrowLeft className="w-5 h-5" />
          </motion.button>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold text-slate-900">
                Monitor #{monitor.id}
              </h1>
              <span className="text-xs font-mono font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-700">
                {monitor.patient_id}
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Assigned to{" "}
              <span className="font-semibold text-slate-700">
                {monitor.patient_name}
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Section 1: Core Protocol Specification */}
      <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-indigo-50 text-indigo-600 rounded-xl">
              {monitor.input_type === "video" ? (
                <Video className="w-5 h-5" />
              ) : (
                <Camera className="w-5 h-5" />
              )}
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800">
                Protocol Specification
              </h2>
              <span className="text-xs text-slate-400 capitalize">
                {monitor.input_type} Telemetry Protocol
              </span>
            </div>
          </div>

          <span className="text-xs font-mono font-bold px-3 py-1 bg-indigo-50 text-indigo-700 rounded-lg flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5" />
            {monitor.time} • {monitor.frequency}
          </span>
        </div>

        <div className="space-y-3">
          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Patient Instructions
            </span>
            <p className="text-sm font-semibold text-slate-800">
              {monitor.instructions}
            </p>
          </div>

          <div className="p-3.5 bg-slate-50 rounded-xl border border-slate-200/80">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Things to Evaluate
            </span>
            <p className="text-xs text-slate-700">
              {monitor.things_to_evaluate}
            </p>
          </div>

          <div className="p-3.5 bg-red-50/70 rounded-xl border border-red-200 text-red-900 flex items-start gap-2">
            <ShieldAlert className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-red-600 block mb-0.5">
                Trigger Alert Condition
              </span>
              <p className="text-xs font-semibold">
                {monitor.trigger_alert_if}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Section 2: Alerts Specific to this Monitor */}
      <section className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-red-50 text-red-600 rounded-xl">
              <AlertTriangle className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-800">
                Protocol Threshold Alerts
              </h2>
              <p className="text-xs text-slate-400">
                Alerts triggered specifically by submissions for this monitor
              </p>
            </div>
          </div>
          <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-red-50 text-red-700">
            {alerts.length} Active
          </span>
        </div>

        {alerts.length === 0 ? (
          <div className="flex items-center gap-2 text-xs text-emerald-600 bg-emerald-50/70 px-4 py-3 rounded-xl border border-emerald-100">
            <ShieldCheck className="w-4 h-4 shrink-0" />
            <span>No active alerts triggered by this monitor protocol.</span>
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

      {/* Section 3: Submissions & Telemetry History for this Monitor */}
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
              Media submitted and evaluated for Monitor #{monitor.id}
            </p>
          </div>
        </div>

        {past_events.length === 0 ? (
          <p className="text-xs text-slate-400 py-3">
            No telemetry recorded for this monitor.
          </p>
        ) : (
          <div className="space-y-3">
            {past_events.map((event) => (
              <div
                key={event.id}
                className={`p-4 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs ${
                  event.alert_triggered_or_not
                    ? "bg-red-50/70 border-red-200"
                    : "bg-slate-50/60 border-slate-200"
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
                      Submitted: {new Date(event.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>

                <span
                  className={`self-start sm:self-auto text-[10px] font-bold px-2.5 py-1 rounded-full uppercase tracking-wider shrink-0 ${
                    event.alert_triggered_or_not
                      ? "bg-red-600 text-white shadow-2xs"
                      : "bg-emerald-100 text-emerald-800"
                  }`}
                >
                  {event.alert_triggered_or_not ? "Alert Triggered" : "Normal"}
                </span>
              </div>
            ))}
          </div>
        )}
      </section>
    </motion.div>
  );
}
