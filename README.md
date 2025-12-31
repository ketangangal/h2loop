# H2Loop - C Code Flowchart Generator
Overview of the system that turns C code into Mermaid flowcharts.

## Architecture (brief)
- Backend: FastAPI (async). In-memory queue + single worker; jobs are lost on restart. Mermaid validation via `mmdc`. LLM generates diagrams.
- Frontend: React + Vite. Uses REST polling for status. WebSocket path exists in codebase but is currently disabled (see TODOs).
- Deployment: Dockerfiles for backend/frontend; docker-compose ties them together.

## Features
| Feature | Status |
|---------|--------|
| Async backend + worker | ✅ |
| Job create/list/detail APIs | ✅ |
| Status updates via HTTP polling | ✅ |
| WebSocket live updates | ⚪ TODO: wire endpoint + broadcast |
| Mermaid validation | ✅ |
| Dockerized frontend/backend | ✅ |
| Health/Live probes | ✅ |

## APIs
- POST `/api/jobs` — submit code.
- GET `/api/jobs` — list jobs.
- GET `/api/jobs/{id}` — job detail.
- GET `/health` — basic health probe.
- GET `/live` — lightweight liveness.
- WebSocket `/ws/jobs/{id}` — TODO: currently disabled; manager exists, endpoint commented.

## Setup
### Automated
```bash
./setup.sh
./run-all.sh   # backend + frontend
```

### Manual
Prereqs: Python 3.8+, Node 18+, npm

Backend:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Docker
```bash
docker-compose up --build
```

## Access
- Frontend: http://localhost:5173 (dev) or http://localhost:3000 (docker)
- Backend API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Notes / TODOs
- WebSocket push is not active: uncomment `/ws/jobs/{id}` in `backend/main.py` and `broadcast_job` calls in `app/services.py`, then add a frontend WebSocket client.
- Jobs are in-memory; restart will drop them. Persist if durability is needed.
- LLM prompt/tooling and ast-grep integration are not documented/absent; add if required by specs.

