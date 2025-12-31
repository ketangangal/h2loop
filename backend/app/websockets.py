import asyncio
from typing import Dict, Set

from fastapi import WebSocket, WebSocketDisconnect

from .models import JobState, to_detail


class JobWebSocketManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}
        self.lock = asyncio.Lock()
        self.loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        async with self.lock:
            self.connections.setdefault(job_id, set()).add(websocket)

    async def disconnect(self, job_id: str, websocket: WebSocket):
        async with self.lock:
            conns = self.connections.get(job_id)
            if conns and websocket in conns:
                conns.remove(websocket)
                if not conns:
                    self.connections.pop(job_id, None)

    async def _broadcast(self, job_id: str, payload: dict):
        conns = list(self.connections.get(job_id, set()))
        for ws in conns:
            try:
                await ws.send_json(payload)
            except WebSocketDisconnect:
                await self.disconnect(job_id, ws)
            except Exception:
                await self.disconnect(job_id, ws)

    def broadcast_job(self, job: JobState):
        payload = {
            "type": "job_update",
            "job": to_detail(job).model_dump(by_alias=True),
        }
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self._broadcast(job.id, payload), self.loop
            )

    async def send_job(self, job: JobState):
        payload = {
            "type": "job_update",
            "job": to_detail(job).model_dump(by_alias=True),
        }
        await self._broadcast(job.id, payload)


manager = JobWebSocketManager()

