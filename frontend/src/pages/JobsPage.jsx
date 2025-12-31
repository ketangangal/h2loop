import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchJobs } from '../api.js';

/**
 * Job list page showing all jobs with basic status/progress.
 * Auto-refreshes every 4 seconds to show updated statuses.
 * TODO: Add filtering by status (active/completed/failed).
 * TODO: Add pagination if job count grows large.
 * TODO: Replace polling with WebSocket subscription for live list updates.
 */
export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  /**
   * Fetch all jobs from backend.
   * Called on mount and by polling interval (4s).
   */
  const load = async () => {
    try {
      const data = await fetchJobs();
      setJobs(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // TODO: Use WebSocket or server-sent events for push updates; polling keeps it simple for now.
    const interval = setInterval(load, 4000);
    return () => clearInterval(interval);
  }, []);

  return (
    <section className="card">
      <div className="card-header">
        <h1>Jobs</h1>
        <button onClick={load}>Refresh</button>
      </div>
      {loading && <p>Loading…</p>}
      {error && <div className="error">{error}</div>}
      <ul className="job-list">
        {jobs.map((job) => (
          <li key={job.id} className="job-row">
            <div>
              <div className="job-title">
                <Link to={`/jobs/${job.id}`}>{job.id}</Link>
              </div>
              <div className="job-meta">
                Status: {job.status} • {job.processedFunctions} /
                {job.totalFunctions}
              </div>
            </div>
            <Link to={`/jobs/${job.id}`} className="ghost-btn">
              Open
            </Link>
          </li>
        ))}
        {!loading && jobs.length === 0 && <p>No jobs yet.</p>}
      </ul>
    </section>
  );
}

