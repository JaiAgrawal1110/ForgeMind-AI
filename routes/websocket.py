from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.logger import log
import asyncio
import json
import random
from datetime import datetime

router = APIRouter()

active_connections: dict = {}

@router.websocket("/telemetry/{machine_id}")
async def telemetry_stream(websocket: WebSocket, machine_id: str):
    await websocket.accept()
    log.info(f"WebSocket connected: {machine_id}")

    if machine_id not in active_connections:
        active_connections[machine_id] = []
    active_connections[machine_id].append(websocket)

    try:
        while True:
            reading = {
                "machine_id": machine_id,
                "temperature": round(random.uniform(60, 85), 2),
                "spindle_speed": round(random.uniform(1000, 3000), 2),
                "machine_state": "running",
                "timestamp": datetime.utcnow().isoformat()
            }
            await websocket.send_text(json.dumps(reading))
            log.info(f"Sent telemetry to {machine_id}: temp={reading['temperature']}°C")
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        active_connections[machine_id].remove(websocket)
        log.info(f"WebSocket disconnected: {machine_id}")