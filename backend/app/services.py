import asyncio
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from fastapi import HTTPException

from .llm import LLMClient
from .models import FunctionResult, JobState, JobStatus
# from .websockets import manager

jobs: Dict[str, JobState] = {}

job_queue: "asyncio.Queue[str]" = asyncio.Queue()
jobs_lock = asyncio.Lock()
llm_client = LLMClient()
worker_task: asyncio.Task | None = None


def _now() -> datetime:
    return datetime.utcnow()


async def enqueue_job(code: str) -> JobState:
    job_id = uuid.uuid4().hex
    job = JobState(id=job_id, code=code, status=JobStatus.SUBMITTED)
    async with jobs_lock:
        jobs[job_id] = job
    await job_queue.put(job_id)
    return job


async def list_jobs() -> List[JobState]:
    async with jobs_lock:
        return list(jobs.values())


async def get_job(job_id: str) -> JobState:
    async with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


async def update_job(job_id: str, **kwargs):
    async with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return
        for key, value in kwargs.items():
            setattr(job, key, value)
        job.updated_at = _now()
        # manager.broadcast_job(job)

async def validate_mermaid(mermaid_text: str) -> bool:
    """Validate Mermaid syntax using mmdc CLI (async)"""
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            inp = Path(tmpdir) / "diagram.mmd"
            out = Path(tmpdir) / "diagram.svg"
            inp.write_text(mermaid_text)
            
            # Use asyncio subprocess for non-blocking execution
            process = await asyncio.create_subprocess_exec(
                "mmdc", "-i", str(inp), "-o", str(out),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
    except FileNotFoundError:
        return False
    except Exception:
        return False


async def process_job(job_id: str):
    """Process a single job asynchronously"""
    job = await get_job(job_id)
    
    # Step 1: Processing started
    await update_job(job_id, status=JobStatus.PROCESSING, total_functions=1, updated_at=_now())
    
    try:
        # Step 2: Generating flowchart with LLM
        await update_job(job_id, status=JobStatus.GENERATING_FLOWCHART)
        print(f"[Job {job_id}] Generating flowchart with LLM...")
        mermaid = await llm_client.generate_from_code(job.code)
        
        # Step 3: Validating Mermaid syntax
        await update_job(job_id, status=JobStatus.VALIDATING)
        print(f"[Job {job_id}] Validating Mermaid syntax...")
        valid = await validate_mermaid(mermaid)
        
        # Step 4: Storing results
        job = await get_job(job_id)
        job.functions.append(
            FunctionResult(
                name="flowchart",
                mermaid=mermaid,
                validated=valid,
                error=None if valid else "Mermaid validation failed",
            )
        )
        
        # Step 5: Completed successfully
        await update_job(
            job_id,
            processed_functions=1,
            status=JobStatus.COMPLETED
        )
        print(f"[Job {job_id}] Completed successfully!")
        
    except Exception as exc:
        print(f"[Job {job_id}] Failed: {exc}")
        await update_job(job_id, status=JobStatus.FAILED, error=str(exc))


async def worker():
    """Background worker that processes jobs from the queue"""
    print("[Worker] Started async worker")
    while True:
        job_id = await job_queue.get()
        try:
            await process_job(job_id)
        except Exception as exc:
            print(f"[Worker] Unexpected error processing job {job_id}: {exc}")
        finally:
            job_queue.task_done()


def start_worker():
    """Start the background worker task"""
    global worker_task
    if worker_task is None or worker_task.done():
        worker_task = asyncio.create_task(worker())
        print("[Worker] Background worker task created")

