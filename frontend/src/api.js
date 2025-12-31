/**
 * API client for backend REST and (future) WebSocket endpoints.
 * Uses axios for HTTP calls; configurable base URL via env.
 * TODO: Add request interceptor for auth tokens if auth is added.
 * TODO: Add retry logic for transient network failures.
 */
import axios from 'axios';

export const API_BASE =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// TODO: Add WebSocket helper when backend WS is enabled.
// Example: export function openJobWebSocket(jobId) { return new WebSocket(`ws://.../ws/jobs/${jobId}`); }

/**
 * Create a new job by submitting C code.
 * Returns job summary with ID; job processes async in background.
 */
export async function createJob(code) {
  const res = await axios.post(`${API_BASE}/api/jobs`, { code });
  return res.data;
}

/**
 * Fetch list of all jobs (summary view).
 * NOTE: Returns full list; no pagination yet.
 */
export async function fetchJobs() {
  const res = await axios.get(`${API_BASE}/api/jobs`);
  return res.data;
}

/**
 * Fetch detailed job information including code and flowcharts.
 * Throws if job ID not found (404).
 */
export async function fetchJob(id) {
  const res = await axios.get(`${API_BASE}/api/jobs/${id}`);
  return res.data;
}

