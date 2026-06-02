# ============================================================
# websocket.py — Real-time telemetry streaming via WebSocket
# Base URL: /ws
#
# ws://localhost:8000/ws/telemetry/{machine_id}
#
# Every 2 seconds:
# 1. Generate telemetry reading
# 2. Run through AI anomaly detection model
# 3. If anomaly detected → create alert in MongoDB
# 4. Push reading + anomaly result to frontend
# ============================================================

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.logger import log
from app.database import get_db
from models.alert import Alert
from ml.anomaly_model import predict as run_predict
import asyncio
import json
import random
from datetime import datetime

router = APIRouter()

# Store active connections
active_connections: dict = {}


@router.websocket("/telemetry/{machine_id}")
async def telemetry_stream(websocket: WebSocket, machine_id: str):
    await websocket.accept()
    log.info(f"WebSocket connected: {machine_id}")

    if machine_id not in active_connections:
        active_connections[machine_id] = []
    active_connections[machine_id].append(websocket)

    # Track consecutive high temp readings for threshold-based alerts
    high_temp_count = 0

    try:
        while True:
            # Step 1: Generate telemetry reading
            # Occasionally inject anomaly for demo purposes (5% chance)
            inject_anomaly = random.random() < 0.05

            if inject_anomaly:
                temperature = round(random.uniform(92, 110), 2)   # Too hot
                spindle_speed = round(random.uniform(400, 600), 2) # Too slow
                vibration = round(random.uniform(1.5, 2.5), 2)     # High vibration
                power_consumption = round(random.uniform(650, 750), 2)
            else:
                temperature = round(random.uniform(62, 82), 2)     # Normal
                spindle_speed = round(random.uniform(1200, 2800), 2)
                vibration = round(random.uniform(0.2, 0.4), 2)
                power_consumption = round(random.uniform(470, 530), 2)

            reading = {
                "machine_id": machine_id,
                "temperature": temperature,
                "spindle_speed": spindle_speed,
                "vibration": vibration,
                "power_consumption": power_consumption,
                "machine_state": "running",
                "timestamp": datetime.utcnow().isoformat()
            }

            # Step 2: Run AI anomaly detection
            is_anomaly, score, confidence = run_predict(
                temperature=temperature,
                spindle_speed=spindle_speed,
                vibration=vibration,
                power_consumption=power_consumption
            )

            # Add AI result to the reading
            reading["anomaly"] = bool(is_anomaly)
            reading["anomaly_score"] = float(score)
            reading["confidence"] = confidence

            # Step 3: Threshold check — temp > 90 for 3 consecutive readings
            if temperature > 90:
                high_temp_count += 1
            else:
                high_temp_count = 0

            threshold_alert = high_temp_count >= 3

            # Step 4: Create alert in MongoDB if anomaly detected
            if is_anomaly or threshold_alert:
                db = get_db()
                alert_type = "threshold" if threshold_alert else "anomaly"
                severity = "critical" if threshold_alert else ("high" if score > 0.7 else "medium")
                message = (
                    f"Temperature exceeded 90°C for 3 consecutive readings"
                    if threshold_alert
                    else f"AI anomaly detected — score: {score}, confidence: {confidence}"
                )

                alert = Alert(
                    machine_id=machine_id,
                    alert_type=alert_type,
                    severity=severity,
                    message=message,
                    anomaly_score=score
                )
                await db["alerts"].insert_one(alert.model_dump())
                log.warning(f"Alert created — {machine_id} | {severity} | {message}")

            # Step 5: Push reading to frontend
            await websocket.send_text(json.dumps(reading))
            log.info(f"Sent telemetry to {machine_id}: temp={temperature}°C | anomaly={is_anomaly}")

            await asyncio.sleep(2)

    except WebSocketDisconnect:
        active_connections[machine_id].remove(websocket)
        log.info(f"WebSocket disconnected: {machine_id}")