import os
from dotenv import load_dotenv
path = os.path.join(os.path.dirname(__file__), ".env")
print("Path", path)
load_dotenv(dotenv_path=path)

from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException  # WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.models import (
    CreateJobRequest,
    JobDetailResponse,
    JobSummaryResponse,
    to_detail,
    to_summary,
)
from app.services import enqueue_job, get_job, list_jobs, start_worker
# from app.websockets import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kick off the background worker on startup. No persistence, so jobs are volatile.
    # TODO: wire manager loop + WebSocket broadcast when push updates are enabled.
    # manager.set_loop(asyncio.get_running_loop())
    start_worker()
    yield


app = FastAPI(
    title="C Function Flowchart Generator",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Basic health probe for container/liveness checks."""
    return {"status": "ok"}


@app.get("/live")
async def live():
    """
    Lightweight readiness-style endpoint.
    NOTE: does not verify worker backlog; add metrics if needed.
    """
    return {"status": "live"}


@app.post("/api/jobs", response_model=JobSummaryResponse)
async def create_job(payload: CreateJobRequest):
    """
    Create a new job to generate flowchart from C code.
    Returns job summary immediately; processing happens async in background.
    TODO: Add rate limiting per client IP to prevent abuse.
    TODO: Add authentication/authorization if exposing publicly.
    """
    if not payload.code or not payload.code.strip():
        raise HTTPException(status_code=400, detail="Code is required")
    job = await enqueue_job(payload.code)
    return to_summary(job)


@app.get("/api/jobs", response_model=List[JobSummaryResponse])
async def list_jobs_endpoint():
    """
    List all jobs with summary information (status, progress).
    NOTE: Returns full list; add pagination if job count grows large.
    """
    jobs = await list_jobs()
    return [to_summary(job) for job in jobs]


@app.get("/api/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job_endpoint(job_id: str):
    """
    Get detailed job information including code, status, and generated flowcharts.
    Raises 404 if job_id not found (in-memory store only).
    """
    job = await get_job(job_id)
    return to_detail(job)


# TODO: Enable WebSockets once broadcast wiring is completed.
# @app.websocket("/ws/jobs/{job_id}")
# async def job_updates(websocket: WebSocket, job_id: str):
#     await websocket.accept()
#     
#     try:
#         job = await get_job(job_id)
#     except HTTPException:
#         await websocket.close(code=4004)  # 4004 = Not Found
#         return
#
#     # Add to connections (websocket already accepted)
#     async with manager.lock:
#         manager.connections.setdefault(job_id, set()).add(websocket)
#     
#     await manager.send_job(job)
#
#     try:
#         while True:
#             # We only expect server-to-client pushes; keep alive otherwise.
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         await manager.disconnect(job_id, websocket)
#     except Exception:
#         await manager.disconnect(job_id, websocket)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)