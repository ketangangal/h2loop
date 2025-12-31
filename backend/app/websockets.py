import asyncio
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from .models import JobState, to_detail


class JobWebSocketManager:
    """
    Manages WebSocket connections for real-time job status updates.
    Groups connections by job_id; broadcasts updates to all clients watching a job.
    TODO: Currently unused; enable in main.py and services.py to activate push updates.
    """
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()
        self.loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        """
        Store event loop for thread-safe coroutine scheduling.
        Must be called from lifespan startup before broadcast_job is used.
        """
        self.loop = loop

    async def connect(self, job_id: str, websocket: WebSocket):
        """
        Accept and register a WebSocket for job updates.
        Called from WebSocket endpoint after validation.
        """
        await websocket.accept()
        async with self.lock:
            self.connections.setdefault(job_id, set()).add(websocket)

    async def disconnect(self, job_id: str, websocket: WebSocket):
        """
        Remove WebSocket from connections; cleanup job_id key if empty.
        """
        async with self.lock:
            conns = self.connections.get(job_id)
            if conns and websocket in conns:
                conns.remove(websocket)
                if not conns:
                    self.connections.pop(job_id, None)

    async def _broadcast(self, job_id: str, payload: dict):
        """
        Send JSON payload to all WebSockets watching this job_id.
        Automatically disconnects failed sockets.
        """
        conns = list(self.connections.get(job_id, set()))
        for ws in conns:
            try:
                await ws.send_json(payload)
            except WebSocketDisconnect:
                await self.disconnect(job_id, ws)
            except Exception:
                await self.disconnect(job_id, ws)

    def broadcast_job(self, job: JobState):
        """
        Thread-safe broadcast from sync context (e.g., worker thread).
        Serializes job to JSON and pushes to all connected clients.
        NOTE: No-op if loop is unset; caller must ensure set_loop was invoked.
        """
        payload = {
            "type": "job_update",
            "job": to_detail(job).model_dump(by_alias=True),
        }
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self._broadcast(job.id, payload), self.loop
            )
        # NOTE: No-op if loop is unset; caller must ensure set_loop was invoked.

    async def send_job(self, job: JobState):
        """
        Async broadcast from within async context (e.g., WebSocket endpoint).
        Sends initial job state to newly connected client.
        """
        payload = {
            "type": "job_update",
            "job": to_detail(job).model_dump(by_alias=True),
        }
        await self._broadcast(job.id, payload)


manager = JobWebSocketManager()

