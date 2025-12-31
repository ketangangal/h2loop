# H2Loop - C Code Flowchart Generator

Full-stack application that accepts C code and generates Mermaid flowcharts using LLM. Built with FastAPI (async) + React, with Docker support.

## 🚀 Quick Start

### Automated Setup (Recommended)

```bash
./setup.sh
./run-all.sh  # Starts both backend and frontend
```

The setup script will:
- ✅ Create Python virtual environment
- ✅ Install Python dependencies
- ✅ Install npm dependencies
- ✅ Create `.env` file with template
- ✅ Provide helpful next steps

### Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Architecture

### Backend (FastAPI - Fully Async)
- **Async/await throughout**: Non-blocking I/O for better concurrency
- **Background worker**: `asyncio.Task` processes jobs from queue
- **Job statuses**: `submitted` → `processing` → `generating_flowchart` → `validating` → `completed`
- **LLM Integration**: Azure OpenAI via LangChain (async `ainvoke`)
- **Validation**: Mermaid syntax validation using `mmdc` CLI (async subprocess)
- **Auto-polling**: Frontend polls every 2 seconds for live updates

### Frontend (React + Vite)
- **Job submission**: Submit C code via textarea or file upload
- **Live updates**: Auto-polling shows real-time job progress
- **Status tracking**: Visual indicators for each processing stage
- **Code display**: Shows original C code alongside flowchart
- **Mermaid rendering**: Interactive flowchart visualization

## Manual Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Configuration

Create `backend/.env` (optional - uses stub if not configured):
```env
AZURE_API_KEY=your-api-key-here
AZURE_API_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_DEPLOYMENT=your-deployment-name
AZURE_API_VERSION=2024-06-01
```

### Running

**Backend:**
```bash
cd backend
source .venv/bin/activate
python main.py
```

**Frontend:**
```bash
cd frontend
npm run dev
```

## 🐳 Docker Deployment

```bash
docker-compose up --build
```

- **Backend**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## 📡 API Endpoints

- `POST /api/jobs` - Submit C code for analysis
  ```json
  { "code": "int main() { return 0; }" }
  ```
  Returns: Job summary with ID and status

- `GET /api/jobs` - List all jobs with progress

- `GET /api/jobs/{id}` - Get detailed job status and results

## 🎯 Features

✅ **Fully Async Backend** - Non-blocking I/O for better performance  
✅ **Live Status Updates** - Real-time progress tracking (6 stages)  
✅ **Auto-polling** - Frontend automatically refreshes active jobs  
✅ **Original Code Display** - Shows submitted code alongside flowchart  
✅ **Mermaid Validation** - Syntax validation with error reporting  
✅ **Quote Sanitization** - Automatic cleanup of problematic characters  
✅ **Stub Mode** - Works without Azure OpenAI configuration  

## 📝 Job Status Flow

```
📝 submitted → ⚙️ processing → 🤖 generating_flowchart → ✅ validating → ✅ completed
```

## 🛠️ Convenience Scripts

- `./setup.sh` - One-time setup
- `./run-backend.sh` - Start backend only
- `./run-frontend.sh` - Start frontend only
- `./run-all.sh` - Start both servers

## ⚙️ Technical Details

### Async Architecture
- `asyncio.Queue` for job queue
- `asyncio.Lock` for thread-safe state management
- `asyncio.create_subprocess_exec` for validation
- `client.ainvoke()` for async LLM calls

### Dependencies
- **Backend**: FastAPI, LangChain, Azure OpenAI, python-dotenv
- **Frontend**: React, Vite, Axios, Mermaid

## 📌 Notes & Limitations

- **In-memory storage**: Job data lost on restart
- **Stub mode**: Returns basic flowchart if Azure OpenAI not configured
- **Mermaid CLI**: Validation requires `mmdc` installed (optional)
- **Auto-polling**: Frontend polls every 2 seconds during active jobs

