import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchJobs } from '../api.js';

export default function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

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

