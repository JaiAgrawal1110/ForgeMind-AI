# ============================================================
# websocket.py — Real-time telemetry streaming via WebSocket
# Base URL: /ws
#
# ws://localhost:8000/ws/telemetry/{machine_id}
#
# Instead of the client asking "what's the data?" every second,
# the SERVER pushes data to the client automatically.
# Like WhatsApp messages vs refreshing email.
#
# NOTE: Basic setup for now (Week 1)
# Full simulation script gets built in Week 2
# ============================================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.logger import log
import asyncio
import json
import random
from datetime import datetime

router = APIRouter()

# Store active connections so we can broadcast to multiple clients
active_connections: dict = {}   # { machine_id: [WebSocket, WebSocket, ...] }


# ------------------------------------------------------------
# WebSocket /ws/telemetry/{machine_id}
# ------------------------------------------------------------
@router.websocket("/telemetry/{machine_id}")
async def telemetry_stream(websocket: WebSocket, machine_id: str):
    """
    Client connects here to receive live telemetry.
    Server pushes a new reading every 2 seconds.

    To test: use a WebSocket client like:
    - Postman (supports WS)
    - wscat (npm install -g wscat)
      wscat -c ws://localhost:8000/ws/telemetry/CNC-001
    """
    await websocket.accept()   # Accept the connection
    log.info(f"WebSocket connected: {machine_id}")

    # Track this connection
    if machine_id not in active_connections:
        active_connections[machine_id] = []
    active_connections[machine_id].append(websocket)

    try:
        while True:
            # Simulate a telemetry reading (Week 2: replace with real Kafka data)
            reading = {
                "machine_id": machine_id,
                "temperature": round(random.uniform(60, 85), 2),     # Normal range
                "spindle_speed": round(random.uniform(1000, 3000), 2),
                "machine_state": "running",
                "timestamp": datetime.utcnow().isoformat()
            }

            # Push to client
            await websocket.send_text(json.dumps(reading))
            log.info(f"Sent telemetry to {machine_id}: temp={reading['temperature']}°C")

            await asyncio.sleep(2)    # Send every 2 seconds

    except WebSocketDisconnect:
        # Client disconnected — clean up
        active_connections[machine_id].remove(websocket)
        log.info(f"WebSocket disconnected: {machine_id}")
