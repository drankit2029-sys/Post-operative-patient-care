import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

import Home from './Components/Home';
import AddPatient from './Components/AddPatient';
import Alerts from './Components/Alerts';
import Patients from './Components/Patients';
import PatientDetail from './Components/PatientDetail';
import PatientPastReminders from './Components/PatientPastReminders';
import PatientMonitors from './Components/PatientMonitors';
import PatientMonitor from './Components/PatientMonitor';
import PatientReminder from './Components/PatientReminder';

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Navigate to="/home" replace />} />
        <Route path="/home" element={<Home />} />
        <Route path="/add_patient" element={<AddPatient />} />
        <Route path="/alerts" element={<Alerts />} />
        <Route path="/patients" element={<Patients />} />
        <Route path="/patients/:id" element={<PatientDetail />} />
        <Route path="/patients/:id/reminders" element={<PatientPastReminders />} />
        <Route path="/patients/:id/reminders/:reminder_id" element={<PatientReminder />} />
        <Route path="/patients/:id/monitors" element={<PatientMonitors />} />
        <Route path="/patients/:id/monitors/:monitor_id" element={<PatientMonitor />} />
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <main className="min-h-screen bg-slate-50 text-slate-900 antialiased">
        <AnimatedRoutes />
      </main>
    </BrowserRouter>
  );
}