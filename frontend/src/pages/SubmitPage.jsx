import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createJob } from '../api.js';

export default function SubmitPage() {
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleFile = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (evt) => setCode(evt.target.result || '');
    reader.readAsText(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    if (!code.trim()) {
      setError('Please paste code or choose a file.');
      return;
    }
    setLoading(true);
    try {
      const job = await createJob(code);
      navigate(`/jobs/${job.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h1>Analyze C code</h1>
      <p>Paste C code or upload a .c file to generate flowcharts.</p>
      <form onSubmit={handleSubmit} className="form">
        <label className="label">
          C code
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            rows={14}
            placeholder={"int main(void) { printf(\"Hello\"); return 0; }"}
          />
        </label>
        <label className="label">
          Or upload file
          <input type="file" accept=".c" onChange={handleFile} />
        </label>
        {error && <div className="error">{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Submitting…' : 'Analyze code'}
        </button>
      </form>
    </section>
  );
}

