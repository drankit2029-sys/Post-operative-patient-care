import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Home from "./Components/Home";
import AddPatient from "./Components/AddPatient";
import Alerts from "./Components/Alerts";
import Patients from "./Components/Patients";
import PatientDetail from "./Components/PatientDetail";
import PatientPastReminders from "./Components/PatientPastReminders";
import PatientMonitors from "./Components/PatientMonitors";
import PatientMonitor from "./Components/PatientMonitor";
import PatientReminder from "./Components/PatientReminder";

export default function App() {
  return (
    <BrowserRouter>
      <main className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        <Routes>
          {/* Default redirect to /home */}
          <Route path="/" element={<Navigate to="/home" replace />} />

          {/* Top-level views */}
          <Route path="/home" element={<Home />} />
          <Route path="/add_patient" element={<AddPatient />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/patients" element={<Patients />} />

          {/* Patient dynamic routes */}
          <Route path="/patients/:id" element={<PatientDetail />} />
          <Route
            path="/patients/:id/reminders"
            element={<PatientPastReminders />}
          />
          <Route
            path="/patients/:id/reminders/:reminder_id"
            element={<PatientReminder />}
          />
          <Route path="/patients/:id/monitors" element={<PatientMonitors />} />
          <Route
            path="/patients/:id/monitors/:monitor_id"
            element={<PatientMonitor />}
          />

          {/* Fallback route */}
          <Route path="*" element={<Navigate to="/home" replace />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
