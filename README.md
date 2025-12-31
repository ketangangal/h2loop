# H2Loop - C Code Flowchart Generator

Full-stack application that accepts C code and generates Mermaid flowcharts using LLM. Built with FastAPI (async) + React, with Docker support.

## Features

| Feature | Status |
|---------|--------|
| Fully Async Backend | ✅ |
| Live Status Updates | ✅ |
| Auto-polling | ✅ |
| Original Code Display | ✅ |
| Mermaid Validation | ✅ |

## Setup

### Automated Setup (Recommended)

```bash
./setup.sh
./run-all.sh  # Starts both backend and frontend
```

### Manual Setup

**Prerequisites:**
- Python 3.8+
- Node.js 18+
- npm

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

**Configuration (Optional):**

Create `backend/.env`:
```env
AZURE_API_KEY=your-api-key-here
AZURE_API_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_DEPLOYMENT=your-deployment-name
AZURE_API_VERSION=2024-06-01
```

**Running:**

Backend:
```bash
cd backend
source .venv/bin/activate
python main.py
```

Frontend:
```bash
cd frontend
npm run dev
```

**Docker:**
```bash
docker-compose up --build
```

### Access
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
