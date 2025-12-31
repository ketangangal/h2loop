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

jobs: Dict[str, JobState] = {}  # In-memory; restart loses state.

job_queue: "asyncio.Queue[str]" = asyncio.Queue()  # Single consumer worker; add concurrency if needed.
jobs_lock = asyncio.Lock()
llm_client = LLMClient()
worker_task: asyncio.Task | None = None


def _now() -> datetime:
    return datetime.utcnow()


async def enqueue_job(code: str) -> JobState:
    """
    Create and enqueue a new job for processing.
    Returns JobState immediately; worker picks up from queue.
    NOTE: Jobs stored in-memory only; restart will lose all jobs.
    TODO: Add persistence layer (DB/Redis) for durability.
    """
    job_id = uuid.uuid4().hex
    job = JobState(id=job_id, code=code, status=JobStatus.SUBMITTED)
    async with jobs_lock:
        jobs[job_id] = job
    await job_queue.put(job_id)
    return job


async def list_jobs() -> List[JobState]:
    """
    Return all jobs from in-memory store.
    TODO: Add filtering by status, pagination, and sorting options.
    """
    async with jobs_lock:
        return list(jobs.values())


async def get_job(job_id: str) -> JobState:
    """
    Retrieve a single job by ID.
    Raises HTTPException(404) if not found in memory.
    """
    async with jobs_lock:
        job = jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


async def update_job(job_id: str, **kwargs):
    """
    Update job fields and timestamp; intended for status transitions.
    TODO: Wire broadcast once WebSocket endpoint is enabled.
    TODO: Add validation for allowed status transitions.
    """
    async with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return
        for key, value in kwargs.items():
            setattr(job, key, value)
        job.updated_at = _now()
        # TODO: Wire broadcast once WebSocket endpoint is enabled.
        # manager.broadcast_job(job)

async def validate_mermaid(mermaid_text: str) -> bool:
    """
    Validate Mermaid syntax using mmdc CLI (async subprocess).
    Returns False on any error (missing CLI, parse error, etc).
    NOTE: Silently fails; stderr not surfaced to caller.
    TODO: Capture and return stderr for debugging parse errors.
    TODO: Add timeout to prevent long-running validations.
    """
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
    """
    Process a single job through the pipeline:
    1. PROCESSING → 2. GENERATING_FLOWCHART → 3. VALIDATING → 4. COMPLETED/FAILED
    Each status update triggers a state change visible to polling clients.
    TODO: Add retry logic with exponential backoff for LLM failures.
    TODO: Add timeout for entire job to prevent infinite hangs.
    TODO: Consider parsing C code with ast-grep before LLM call.
    """
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
    """
    Background worker that processes jobs from the queue.
    Single consumer; blocks on empty queue.
    NOTE: Never exits; no graceful shutdown handling.
    TODO: Support cancellation on app shutdown.
    TODO: Add multiple workers for concurrency if needed.
    """
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
    """
    Start the background worker task from lifespan startup.
    Idempotent: only creates task if none exists or previous is done.
    TODO: Store task reference and cancel on shutdown for clean exit.
    """
    global worker_task
    if worker_task is None or worker_task.done():
        worker_task = asyncio.create_task(worker())
        print("[Worker] Background worker task created")

