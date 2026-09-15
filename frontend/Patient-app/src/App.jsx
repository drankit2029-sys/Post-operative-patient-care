import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Pill,
  Activity,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Send,
  History,
  Sparkles,
  User,
  ChevronDown,
  Check,
  Users,
} from "lucide-react";
import {
  getPatientsList,
  getTodayTasks,
  completeReminderTask,
  submitMonitorTask,
  getPatientHistory,
} from "./api";
import TelemetryModal from "./Components/TelemetryModal";

export default function App() {
  const [patients, setPatients] = useState([]);
  const [patientId, setPatientId] = useState("");
  const [activeTab, setActiveTab] = useState("today");
  const [loading, setLoading] = useState(true);
  const [taskData, setTaskData] = useState(null);
  const [historyData, setHistoryData] = useState({ pastReminders: [], pastMonitors: [] });
  const [activeTelemetryTask, setActiveTelemetryTask] = useState(null);
  const [notificationBanner, setNotificationBanner] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // 1. Initial Load: Fetch list of patients
  useEffect(() => {
    async function loadPatients() {
      try {
        const list = await getPatientsList();
        setPatients(list);
        if (list.length > 0) {
          // Default to PT-820 if present, otherwise select the first patient
          const defaultPt = list.find((p) => p.patient_id === "PT-820") || list[0];
          setPatientId(defaultPt.patient_id);
        } else {
          setLoading(false);
        }
      } catch (err) {
        console.error("Failed to load patient directory:", err);
        setLoading(false);
      }
    }
    loadPatients();
  }, []);

  // 2. Fetch daily tasks and history whenever selected patient changes
  const fetchTasks = async (id) => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await getTodayTasks(id);
      setTaskData(data);
      const history = await getPatientHistory(id);
      setHistoryData(history);
    } catch (err) {
      console.error("Failed to load patient tasks:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (patientId) {
      fetchTasks(patientId);
    }
  }, [patientId]);

  const handlePatientChange = (newId) => {
    setPatientId(newId);
    setIsDropdownOpen(false);
  };

  const handleConfirmDose = async (taskId) => {
    try {
      await completeReminderTask(taskId);
      setNotificationBanner("Medication dose verified and logged!");
      setTimeout(() => setNotificationBanner(null), 4000);
      fetchTasks(patientId);
    } catch (err) {
      alert("Failed to confirm medication dose.");
    }
  };

  const handleTelemetrySuccess = async (taskId, payload) => {
    await submitMonitorTask(taskId, payload);
    setNotificationBanner("Telemetry check submitted and clinically evaluated!");
    setTimeout(() => setNotificationBanner(null), 4000);
    fetchTasks(patientId);
  };

  const getGracePeriodStatus = (scheduledTimeStr) => {
    const [hours, minutes] = scheduledTimeStr.split(":").map(Number);
    const now = new Date();
    const scheduled = new Date();
    scheduled.setHours(hours, minutes, 0, 0);

    const diffMinutes = Math.floor((now - scheduled) / 60000);

    if (diffMinutes < 0) {
      return { label: `Scheduled for ${scheduledTimeStr}`, isUrgent: false };
    } else if (diffMinutes <= 30) {
      return {
        label: `${30 - diffMinutes}m left in grace window`,
        isUrgent: true,
      };
    } else {
      return { label: "Lapsed past 30m window", isUrgent: false, isOverdue: true };
    }
  };

  const currentPatientMeta = patients.find((p) => p.patient_id === patientId);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans pb-12">
      {/* Patient Header with Dynamic Switcher */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-2xs">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between gap-3">
          {/* Patient Selector */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-2.5 p-1.5 -ml-1.5 rounded-2xl hover:bg-slate-50 transition-colors text-left group"
            >
              <div className="w-10 h-10 rounded-2xl bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-xs shrink-0">
                <User className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <h1 className="text-sm font-bold text-slate-900 leading-tight group-hover:text-indigo-600 transition-colors">
                    {taskData?.patient_name || currentPatientMeta?.name || "Select Patient"}
                  </h1>
                  <span className="text-[10px] font-mono font-bold bg-indigo-50 text-indigo-700 px-1.5 py-0.5 rounded">
                    {patientId || "N/A"}
                  </span>
                  <ChevronDown
                    className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
                      isDropdownOpen ? "rotate-180 text-indigo-600" : ""
                    }`}
                  />
                </div>
                <p className="text-[11px] text-slate-400 truncate max-w-[200px] sm:max-w-xs">
                  {currentPatientMeta?.final_diagnosis || "Post-Discharge Care"}
                </p>
              </div>
            </button>

            {/* Switcher Dropdown */}
            <AnimatePresence>
              {isDropdownOpen && (
                <motion.div
                  initial={{ opacity: 0, y: 8, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: 8, scale: 0.98 }}
                  transition={{ duration: 0.15 }}
                  className="absolute left-0 mt-2 w-72 sm:w-80 bg-white rounded-2xl shadow-xl border border-slate-200 p-2 z-50 space-y-1"
                >
                  <div className="px-3 py-1.5 flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                    <span className="flex items-center gap-1">
                      <Users className="w-3.5 h-3.5" /> Registered Patients
                    </span>
                    <span>{patients.length} Total</span>
                  </div>

                  <div className="max-h-60 overflow-y-auto space-y-1">
                    {patients.map((p) => {
                      const isSelected = p.patient_id === patientId;
                      return (
                        <button
                          key={p.patient_id}
                          onClick={() => handlePatientChange(p.patient_id)}
                          className={`w-full p-2.5 rounded-xl text-left flex items-center justify-between transition-colors ${
                            isSelected
                              ? "bg-indigo-50/80 text-indigo-900 font-semibold"
                              : "hover:bg-slate-50 text-slate-700"
                          }`}
                        >
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className="text-xs font-bold">{p.name}</span>
                              <span className="text-[10px] font-mono px-1 rounded bg-slate-100 text-slate-600">
                                {p.patient_id}
                              </span>
                            </div>
                            <span className="text-[10px] text-slate-400 block truncate max-w-[220px]">
                              {p.final_diagnosis || "Under Observation"}
                            </span>
                          </div>
                          {isSelected && <Check className="w-4 h-4 text-indigo-600 shrink-0" />}
                        </button>
                      );
                    })}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Navigation Tab Pills */}
          <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl text-xs font-semibold shrink-0">
            <button
              onClick={() => setActiveTab("today")}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === "today"
                  ? "bg-white text-indigo-600 shadow-2xs"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Today
            </button>
            <button
              onClick={() => setActiveTab("history")}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === "history"
                  ? "bg-white text-indigo-600 shadow-2xs"
                  : "text-slate-500 hover:text-slate-900"
              }`}
            >
              Feedback
            </button>
          </div>
        </div>
      </header>

      {/* Notification Toast */}
      <AnimatePresence>
        {notificationBanner && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-3xl mx-auto px-4 mt-3"
          >
            <div className="p-3 bg-emerald-600 text-white text-xs font-semibold rounded-2xl shadow-md flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
              <span>{notificationBanner}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <main className="max-w-3xl mx-auto px-4 pt-5 space-y-6">
        {loading ? (
          <div className="py-24 flex flex-col items-center justify-center text-slate-400 gap-2">
            <Clock className="w-7 h-7 animate-spin text-indigo-600" />
            <span className="text-xs font-medium">Fetching recovery schedule...</span>
          </div>
        ) : activeTab === "today" ? (
          <>
            {/* Medications Reminders */}
            <section className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-indigo-50 text-indigo-600 rounded-lg">
                    <Pill className="w-4 h-4" />
                  </div>
                  <h2 className="text-sm font-bold text-slate-800">Prescribed Medications</h2>
                </div>
                <span className="text-xs text-slate-400 font-medium">
                  {taskData?.reminders.filter((r) => r.status === "completed").length} /{" "}
                  {taskData?.reminders.length || 0} Completed
                </span>
              </div>

              <div className="space-y-2.5">
                {!taskData?.reminders || taskData.reminders.length === 0 ? (
                  <p className="text-xs text-slate-400 py-4 text-center bg-white rounded-2xl border border-slate-200">
                    No medication reminders scheduled for today.
                  </p>
                ) : (
                  taskData.reminders.map((task) => {
                    const grace = getGracePeriodStatus(task.time);
                    const isPending = task.status === "pending";
                    const isCompleted = task.status === "completed";

                    return (
                      <div
                        key={task.task_id}
                        className={`p-4 rounded-2xl border transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${
                          isCompleted
                            ? "bg-slate-50/80 border-slate-200 text-slate-500"
                            : grace.isUrgent
                            ? "bg-amber-50/80 border-amber-300 shadow-2xs"
                            : "bg-white border-slate-200 shadow-2xs"
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <span
                            className={`px-2.5 py-1 rounded-xl text-xs font-mono font-bold flex items-center gap-1 ${
                              isCompleted
                                ? "bg-slate-200 text-slate-600"
                                : grace.isUrgent
                                ? "bg-amber-200 text-amber-900"
                                : "bg-indigo-50 text-indigo-700"
                            }`}
                          >
                            <Clock className="w-3 h-3" />
                            {task.time}
                          </span>

                          <div>
                            <h3
                              className={`text-sm font-bold ${
                                isCompleted ? "line-through text-slate-400" : "text-slate-800"
                              }`}
                            >
                              {task.content}
                            </h3>
                            <span className="text-[11px] font-medium text-slate-400 block mt-0.5">
                              {isCompleted ? "Confirmed taken" : grace.label}
                            </span>
                          </div>
                        </div>

                        {isPending && (
                          <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.97 }}
                            onClick={() => handleConfirmDose(task.task_id)}
                            className={`px-4 py-2 rounded-xl text-xs font-semibold text-white shadow-2xs transition-colors flex items-center justify-center gap-1.5 ${
                              grace.isUrgent
                                ? "bg-amber-600 hover:bg-amber-700"
                                : "bg-indigo-600 hover:bg-indigo-700"
                            }`}
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Confirm Taken
                          </motion.button>
                        )}

                        {isCompleted && (
                          <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full self-start sm:self-auto">
                            Taken
                          </span>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </section>

            {/* Telemetry Monitors */}
            <section className="space-y-3 pt-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 bg-rose-50 text-rose-600 rounded-lg">
                    <Activity className="w-4 h-4" />
                  </div>
                  <h2 className="text-sm font-bold text-slate-800">Recovery Telemetry Checks</h2>
                </div>
                <span className="text-xs text-slate-400 font-medium">
                  {taskData?.monitors.filter((m) => m.status === "completed").length} /{" "}
                  {taskData?.monitors.length || 0} Evaluated
                </span>
              </div>

              <div className="space-y-3">
                {!taskData?.monitors || taskData.monitors.length === 0 ? (
                  <p className="text-xs text-slate-400 py-4 text-center bg-white rounded-2xl border border-slate-200">
                    No visual or mobility checks required today.
                  </p>
                ) : (
                  taskData.monitors.map((task) => {
                    const isCompleted = task.status === "completed";

                    return (
                      <div
                        key={task.task_id}
                        className={`p-5 rounded-2xl border transition-all flex flex-col gap-3 ${
                          isCompleted
                            ? "bg-slate-50 border-slate-200"
                            : "bg-white border-slate-200 shadow-2xs"
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded">
                              {task.input_type} Telemetry • {task.time}
                            </span>
                            <h3 className="text-sm font-bold text-slate-900 mt-1.5">
                              {task.instructions}
                            </h3>
                            <p className="text-xs text-slate-500 mt-0.5">
                              {task.things_to_evaluate}
                            </p>
                          </div>

                          {isCompleted ? (
                            <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full shrink-0">
                              Evaluated
                            </span>
                          ) : (
                            <button
                              onClick={() => setActiveTelemetryTask(task)}
                              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold shadow-2xs flex items-center gap-1.5 shrink-0"
                            >
                              <Send className="w-3.5 h-3.5" />
                              Perform Check
                            </button>
                          )}
                        </div>

                        {task.user_notes && (
                          <div className="text-[11px] bg-white p-2.5 rounded-xl border border-slate-100 text-slate-600 italic">
                            Reported: "{task.user_notes}"
                          </div>
                        )}
                      </div>
                    );
                  })
                )}
              </div>
            </section>
          </>
        ) : (
          /* Feedback & Clinical History */
          <section className="space-y-4">
            <div className="flex items-center gap-2 pb-2 border-b border-slate-200">
              <History className="w-4 h-4 text-indigo-600" />
              <h2 className="text-sm font-bold text-slate-800">Clinical Evaluation Feedback</h2>
            </div>

            {historyData.pastMonitors.length === 0 && historyData.pastReminders.length === 0 ? (
              <p className="text-xs text-slate-400 py-6 text-center">
                No past checks or remarks recorded yet.
              </p>
            ) : (
              <div className="space-y-3">
                {historyData.pastMonitors.map((event) => (
                  <div
                    key={event.id}
                    className={`p-4 rounded-2xl border text-xs ${
                      event.alert_triggered_or_not
                        ? "bg-red-50/70 border-red-200 text-red-900"
                        : "bg-white border-slate-200 text-slate-700 shadow-2xs"
                    }`}
                  >
                    <div className="flex items-center justify-between font-bold mb-1">
                      <span className="flex items-center gap-1.5">
                        {event.alert_triggered_or_not ? (
                          <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
                        ) : (
                          <Sparkles className="w-4 h-4 text-indigo-600 shrink-0" />
                        )}
                        {event.alert_triggered_or_not ? "Clinical Flag Raised" : "Check-in Normal"}
                      </span>
                      <span className="text-[10px] text-slate-400 font-normal">
                        {new Date(event.created_at).toLocaleTimeString([], {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </span>
                    </div>
                    <p className="mt-1 leading-relaxed">{event.remark}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        )}
      </main>

      {/* Telemetry Upload Modal */}
      {activeTelemetryTask && (
        <TelemetryModal
          task={activeTelemetryTask}
          onClose={() => setActiveTelemetryTask(null)}
          onSubmitSuccess={handleTelemetrySuccess}
        />
      )}
    </div>
  );
}