import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchJob } from '../api.js';
import MermaidViewer from '../components/MermaidViewer.jsx';

/**
 * Job detail page showing status, original code, and generated flowcharts.
 * Uses HTTP polling (2s interval) for live updates while job is active.
 * TODO: Replace polling with WebSocket subscription for real-time pushes.
 * TODO: Add download button to export Mermaid/SVG diagrams.
 */
export default function JobDetailPage() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);

  /**
   * Fetch latest job state from backend.
   * Called on mount and by polling interval.
   */
  const load = async () => {
    try {
      const data = await fetchJob(jobId);
      setJob(data);
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  useEffect(() => {
    load();
  }, [jobId]);

  // Auto-polling: refresh every 2 seconds while job is active.
  // TODO: Replace with WebSocket push once backend WS is enabled.
  useEffect(() => {
    const activeStatuses = ['submitted', 'queued', 'processing', 'in_progress', 'generating_flowchart', 'validating'];
    const isActive = activeStatuses.includes(job?.status);
    
    if (!isActive) return;
    
    const interval = setInterval(load, 2000);
    return () => clearInterval(interval);
  }, [job?.status, jobId]);

  /**
   * Map job status to user-friendly display text with emoji.
   * Returns default for unknown statuses.
   */
  const getStatusDisplay = (status) => {
    const statusMap = {
      'submitted': { emoji: '📝', text: 'Submitted', message: 'Job has been submitted and queued for processing' },
      'queued': { emoji: '📝', text: 'Queued', message: 'Job is queued for processing' },
      'processing': { emoji: '⚙️', text: 'Processing', message: 'Job is being processed' },
      'in_progress': { emoji: '⚙️', text: 'In Progress', message: 'Processing in progress' },
      'generating_flowchart': { emoji: '🤖', text: 'Generating Flowchart', message: 'AI is generating the flowchart diagram' },
      'validating': { emoji: '✅', text: 'Validating', message: 'Validating Mermaid syntax' },
      'completed': { emoji: '✅', text: 'Completed', message: 'Job completed successfully' },
      'success': { emoji: '✅', text: 'Success', message: 'Job completed successfully' },
      'failed': { emoji: '❌', text: 'Failed', message: 'Job processing failed' },
    };
    return statusMap[status] || { emoji: '❓', text: status, message: 'Unknown status' };
  };

  const activeStatuses = ['submitted', 'queued', 'processing', 'in_progress', 'generating_flowchart', 'validating'];
  const isActive = activeStatuses.includes(job?.status);

  return (
    <section className="card">
      <div className="card-header">
        <div>
          <h1>Job {jobId}</h1>
          {job && (
            <p>
              Status: <strong>{getStatusDisplay(job.status).emoji} {getStatusDisplay(job.status).text}</strong>
              {job.totalFunctions > 0 && (
                <> • {job.processedFunctions} / {job.totalFunctions}</>
              )}
            </p>
          )}
        </div>
        <button onClick={load}>Refresh</button>
      </div>
      {error && <div className="error">{error}</div>}
      {!job && !error && <p>Loading…</p>}

      {isActive && (
        <p className="status-message">
          {getStatusDisplay(job?.status).emoji} {getStatusDisplay(job?.status).message}
          <span className="polling-indicator"> • Auto-refreshing</span>
        </p>
      )}
      
      {job?.status === 'failed' && (
        <div className="error">
          ❌ Job failed: {job.error}
        </div>
      )}
      
      {(job?.status === 'completed' || job?.status === 'success') && (
        <div className="success-message">
          {getStatusDisplay(job?.status).emoji} {getStatusDisplay(job?.status).message}
        </div>
      )}
      
      {(job?.status === 'completed' || job?.status === 'success') && job.functions.length === 0 && (
        <p>No flowchart generated.</p>
      )}

      {job?.code && (
        <div className="code-section">
          <h2>Original C Code</h2>
          <div className="code-block">
            <pre><code>{job.code}</code></pre>
          </div>
        </div>
      )}

      {job?.functions?.map((fn) => (
        <div key={fn.name} className="function-card">
          <div className="function-header">
            <h2>{fn.name}</h2>
            <span className={fn.validated ? 'badge success' : 'badge warn'}>
              {fn.validated ? 'Validated' : 'Unvalidated'}
            </span>
          </div>
          <div className="function-body">
            <div className="code-block">
              <div className="code-header">Mermaid syntax</div>
              <textarea readOnly value={fn.mermaid} />
            </div>
            <div className="diagram">
              <MermaidViewer chart={fn.mermaid} />
            </div>
          </div>
        </div>
      ))}
    </section>
  );
}

