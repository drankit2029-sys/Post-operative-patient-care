import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Users,
  UserPlus,
  AlertTriangle,
  Phone,
  ChevronRight,
  Bell,
  ArrowUpRight,
} from "lucide-react";
import axios from "axios";

// Animation variants
const pageVariants = {
  initial: { opacity: 0, y: 16 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: [0.25, 1, 0.5, 1] },
  },
  exit: {
    opacity: 0,
    y: -12,
    transition: { duration: 0.2, ease: "easeIn" },
  },
};

const listContainerVariants = {
  initial: { opacity: 0 },
  animate: {
    opacity: 1,
    transition: { staggerChildren: 0.06, delayChildren: 0.1 },
  },
};

const listItemVariants = {
  initial: { opacity: 0, y: 14 },
  animate: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 350, damping: 25 },
  },
};

// Sub-component: Animated Patients Summary Button
export function PatientsCountButton() {
  const navigate = useNavigate();
  const [totalPatients, setTotalPatients] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchPatientCount() {
      try {
        const response = await axios.get("/api/api/v1/patients/count", {
          signal: controller.signal,
        });
        if (typeof response.data?.count === "number") {
          setTotalPatients(response.data.count);
        }
      } catch (err) {
        if (!axios.isCancel(err)) {
          console.error("Failed to fetch patient count:", err);
        }
      }
    }

    fetchPatientCount();

    return () => controller.abort();
  }, []);

  return (
    <motion.button
      whileHover={{ y: -3, scale: 1.008 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 400, damping: 20 }}
      onClick={() => navigate("/patients")}
      className="flex-1 flex items-center justify-between p-6 bg-white border border-slate-200/90 rounded-2xl shadow-sm hover:shadow-md hover:border-indigo-300 transition-colors text-left group relative overflow-hidden"
    >
      <div className="flex items-center gap-4 relative z-10">
        <motion.div
          whileHover={{ rotate: [0, -6, 6, 0] }}
          transition={{ duration: 0.4 }}
          className="p-3.5 bg-indigo-50 text-indigo-600 rounded-xl group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-200"
        >
          <Users className="w-6 h-6" />
        </motion.div>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Total Active
          </span>
          <h3 className="text-2xl font-bold text-slate-800">Patients</h3>
        </div>
      </div>

      <div className="flex items-center gap-3 relative z-10">
        <motion.span
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 300, delay: 0.15 }}
          className="text-3xl font-extrabold text-indigo-600 font-mono"
        >
          {totalPatients}
        </motion.span>
        <motion.div
          animate={{ x: [0, 2, 0] }}
          transition={{ repeat: Infinity, duration: 1.8, ease: "easeInOut" }}
        >
          <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-indigo-600 transition-colors" />
        </motion.div>
      </div>
    </motion.button>
  );
}

// Sub-component: Animated Alerts List
export function AlertsList({ limit }) {
  const navigate = useNavigate();
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function fetchAlerts() {
      try {
        const url = limit
          ? `/api/api/v1/alerts?limit=${limit}`
          : "/api/api/v1/alerts";

        const res = await axios.get(url, { signal: controller.signal });
        setAlerts(res.data);
        setLoading(false);
      } catch (err) {
        if (!axios.isCancel(err)) {
          console.error("Failed to fetch alerts:", err);
          setLoading(false);
        }
      }
    }

    fetchAlerts();

    return () => controller.abort();
  }, [limit]);

  if (loading) {
    return (
      <div className="p-4 text-center text-sm text-slate-400">
        Loading alerts...
      </div>
    );
  }

  if (alerts.length === 0) {
    return (
      <div className="p-4 text-center text-sm text-slate-400">
        No alerts active.
      </div>
    );
  }

  const itemsToDisplay = limit ? alerts.slice(0, limit) : alerts;

  return (
    <motion.div
      variants={listContainerVariants}
      initial="initial"
      animate="animate"
      className="space-y-3"
    >
      {itemsToDisplay.map((alert) => {
        const isCritical = alert.priority.toLowerCase() === "critical";

        return (
          <motion.div
            key={alert.id}
            variants={listItemVariants}
            whileHover={{ y: -2, scale: 1.004 }}
            whileTap={{ scale: 0.99 }}
            transition={{ type: "spring", stiffness: 450, damping: 25 }}
            onClick={() => navigate(`/patients/${alert.patientId}`)}
            className={`p-4 rounded-xl border cursor-pointer shadow-sm transition-shadow duration-200 ${
              isCritical
                ? "bg-red-50/90 border-red-300 hover:border-red-400 hover:shadow-red-100 hover:shadow-md"
                : "bg-white border-slate-200 hover:border-slate-300 hover:shadow-md"
            }`}
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2.5">
                <AlertTriangle
                  className={`w-4 h-4 shrink-0 ${
                    isCritical ? "text-red-600 animate-pulse" : "text-amber-500"
                  }`}
                />
                <span className="font-semibold text-slate-900">
                  {alert.patientName}
                </span>
                <span className="text-xs px-2 py-0.5 rounded bg-slate-100 text-slate-600 font-mono">
                  {alert.patientId}
                </span>
              </div>

              <div className="flex items-center gap-2.5">
                <span
                  className={`text-[11px] font-bold uppercase tracking-wider px-2.5 py-0.5 rounded-full ${
                    isCritical
                      ? "bg-red-600 text-white shadow-sm"
                      : "bg-amber-100 text-amber-800"
                  }`}
                >
                  {alert.priority}
                </span>
                <span className="text-xs text-slate-400">
                  {alert.timestamp}
                </span>
              </div>
            </div>

            <p
              className={`text-sm mb-3 ${
                isCritical ? "text-red-950 font-medium" : "text-slate-600"
              }`}
            >
              {alert.content}
            </p>

            <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-100/80">
              <div className="flex items-center gap-1.5 text-slate-500">
                <Phone className="w-3.5 h-3.5 text-slate-400" />
                <span>
                  Caretaker:{" "}
                  <span className="font-semibold text-slate-700">
                    {alert.caretakerContact}
                  </span>
                </span>
              </div>
              <span className="inline-flex items-center gap-1 font-semibold text-indigo-600 hover:text-indigo-700">
                Patient Details <ArrowUpRight className="w-3.5 h-3.5" />
              </span>
            </div>
          </motion.div>
        );
      })}
    </motion.div>
  );
}

// Default export: Home Page
export default function Home() {
  const navigate = useNavigate();

  return (
    <motion.div
      variants={pageVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      className="max-w-4xl mx-auto px-4 py-8 flex flex-col gap-8"
    >
      {/* Section 1: Navigation & Actions */}
      <section className="flex flex-col sm:flex-row gap-4 items-stretch">
        <PatientsCountButton />

        <motion.button
          whileHover={{ y: -3, scale: 1.008 }}
          whileTap={{ scale: 0.97 }}
          transition={{ type: "spring", stiffness: 400, damping: 50 }}
          onClick={() => navigate("/add_patient")}
          className="flex items-center justify-center gap-3 px-6 py-6 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl shadow-sm hover:shadow-indigo-200 hover:shadow-lg transition-colors sm:w-60 font-semibold group"
        >
          <motion.div
            whileHover={{ rotate: [0, -6, 6, 0] }}
            transition={{ duration: 0.4 }}
          >
            <UserPlus className="w-5 h-5" />
          </motion.div>
          <span>Add Patient</span>
        </motion.button>
      </section>

      {/* Section 2: Alerts Preview */}
      <section className="flex flex-col gap-4">
        <motion.div
          whileHover={{ x: 2 }}
          onClick={() => navigate("/alerts")}
          className="flex items-center justify-between cursor-pointer group select-none py-1"
        >
          <div className="flex items-center gap-3">
            <motion.div
              whileHover={{ rotate: [0, -10, 10, 0] }}
              transition={{ duration: 0.3 }}
              className="p-2 bg-slate-100 rounded-lg group-hover:bg-indigo-50 transition-colors"
            >
              <Bell className="w-5 h-5 text-slate-700 group-hover:text-indigo-600 transition-colors" />
            </motion.div>
            <h2 className="text-xl font-bold text-slate-800 group-hover:text-indigo-600 transition-colors flex items-center gap-2">
              Alerts
              <ChevronRight className="w-4 h-4 text-slate-400 group-hover:translate-x-1 group-hover:text-indigo-600 transition-all" />
            </h2>
          </div>
          <span className="text-xs font-semibold text-slate-400 group-hover:text-indigo-600 transition-colors">
            View All
          </span>
        </motion.div>

        <AlertsList limit={5} />
      </section>
    </motion.div>
  );
}
