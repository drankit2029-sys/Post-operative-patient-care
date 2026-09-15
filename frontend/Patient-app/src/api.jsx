import axios from "axios";

export const getTodayTasks = async (patientId) => {
  const { data } = await axios.get(`/api/api/v1/patients/${patientId}/tasks/today`);
  return data;
};

export const completeReminderTask = async (taskId) => {
  const { data } = await axios.put(`/api/api/v1/tasks/${taskId}`, {
    status: "completed",
    completed_at: new Date().toISOString(),
  });
  return data;
};

export const submitMonitorTask = async (taskId, { inputGiven, userNotes }) => {
  const { data } = await axios.put(`/api/api/v1/monitor-tasks/${taskId}`, {
    status: "completed",
    completed_at: new Date().toISOString(),
    input_given: inputGiven,
    user_notes: userNotes,
  });
  return data;
};

export const getPatientHistory = async (patientId) => {
  const [remindersRes, monitorsRes] = await Promise.all([
    axios.get(`/api/api/v1/patients/${patientId}/reminders`),
    axios.get(`/api/api/v1/patients/${patientId}/monitors`),
  ]);
  return {
    pastReminders: remindersRes.data.past_events || [],
    pastMonitors: monitorsRes.data.past_events || [],
  };
};