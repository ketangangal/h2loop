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


@app.post("/api/jobs", response_model=JobSummaryResponse)
async def create_job(payload: CreateJobRequest):
    if not payload.code or not payload.code.strip():
        raise HTTPException(status_code=400, detail="Code is required")
    job = await enqueue_job(payload.code)
    return to_summary(job)


@app.get("/api/jobs", response_model=List[JobSummaryResponse])
async def list_jobs_endpoint():
    jobs = await list_jobs()
    return [to_summary(job) for job in jobs]


@app.get("/api/jobs/{job_id}", response_model=JobDetailResponse)
async def get_job_endpoint(job_id: str):
    job = await get_job(job_id)
    return to_detail(job)


# @app.websocket("/ws/jobs/{job_id}")
# async def job_updates(websocket: WebSocket, job_id: str):
#     await websocket.accept()
    
#     try:
#         job = get_job(job_id)
#     except HTTPException:
#         await websocket.close(code=4004)  # 4004 = Not Found
#         return

#     # Add to connections (websocket already accepted)
#     async with manager.lock:
#         manager.connections.setdefault(job_id, set()).add(websocket)
    
#     await manager.send_job(job)

#     try:
#         while True:
#             await websocket.receive_text()
#     except WebSocketDisconnect:
#         await manager.disconnect(job_id, websocket)
#     except Exception:
#         await manager.disconnect(job_id, websocket)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)