import axios from 'axios';

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function createJob(code) {
  const res = await axios.post(`${API_BASE}/api/jobs`, { code });
  return res.data;
}

export async function fetchJobs() {
  const res = await axios.get(`${API_BASE}/api/jobs`);
  return res.data;
}

export async function fetchJob(id) {
  const res = await axios.get(`${API_BASE}/api/jobs/${id}`);
  return res.data;
}

