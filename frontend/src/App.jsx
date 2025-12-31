import { Link, Route, Routes, useLocation } from 'react-router-dom';
import SubmitPage from './pages/SubmitPage.jsx';
import JobsPage from './pages/JobsPage.jsx';
import JobDetailPage from './pages/JobDetailPage.jsx';

function Nav() {
  const location = useLocation();
  return (
    <header className="nav">
      <div className="nav-brand">C Flowchart Builder</div>
      <nav>
        <Link className={location.pathname === '/' ? 'active' : ''} to="/">
          New Job
        </Link>
        <Link
          className={location.pathname.startsWith('/jobs') ? 'active' : ''}
          to="/jobs"
        >
          Jobs
        </Link>
      </nav>
    </header>
  );
}

export default function App() {
  return (
    <div className="app">
      <Nav />
      <main className="content">
        <Routes>
          <Route path="/" element={<SubmitPage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/jobs/:jobId" element={<JobDetailPage />} />
        </Routes>
      </main>
    </div>
  );
}

