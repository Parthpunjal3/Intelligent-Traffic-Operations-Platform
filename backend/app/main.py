"""
FastAPI application entrypoint -- Smart City Traffic Management Platform.
"""
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.api import (
    routes_cameras,
    routes_vehicles,
    routes_congestion,
    routes_predictions,
    routes_incidents,
    routes_signals,
    routes_map,
)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_cameras.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_vehicles.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_congestion.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_predictions.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_incidents.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_signals.router, prefix=settings.API_V1_PREFIX)
app.include_router(routes_map.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
def on_startup():
    # For quick local/dev use. In production, use Alembic migrations instead
    # (see backend/README / docs/architecture.md).
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.PROJECT_NAME}


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        for ws in list(self.active):
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                self.disconnect(ws)


manager = ConnectionManager()


@app.websocket("/ws/live")
async def live_updates(ws: WebSocket):
    """
    Frontend subscribes here for push updates (new incidents, congestion
    changes). A background worker/service can call `manager.broadcast(...)`
    whenever new data lands; for simplicity this demo just pings the map
    state periodically.
    """
    await manager.connect(ws)
    try:
        while True:
            await asyncio.sleep(5)
            await ws.send_text(json.dumps({"type": "heartbeat"}))
    except WebSocketDisconnect:
        manager.disconnect(ws)
