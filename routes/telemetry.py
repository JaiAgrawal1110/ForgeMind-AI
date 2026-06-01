# ============================================================
# telemetry.py — Endpoints for storing and fetching sensor data
# Base URL: /telemetry
#
# POST /telemetry                        → store a reading
# GET  /telemetry/{machine_id}          → get last N readings
# GET  /telemetry/{machine_id}/latest   → get the latest reading
# ============================================================

from fastapi import APIRouter, HTTPException, Query
from models.telemetry import TelemetryReading, TelemetryResponse
from app.database import get_db
from app.logger import log
from datetime import datetime

router = APIRouter()

def format_reading(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


# ------------------------------------------------------------
# POST /telemetry — Store a new sensor reading
# ------------------------------------------------------------
@router.post("/")
async def store_telemetry(reading: TelemetryReading):
    """
    Machines (or the simulator script) POST readings here.
    Body example:
    {
        "machine_id": "CNC-001",
        "temperature": 74.2,
        "spindle_speed": 1800,
        "machine_state": "running"
    }
    """
    db = get_db()

    # Make sure machine exists before storing telemetry
    machine = await db["machines"].find_one({"machine_id": reading.machine_id})
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")

    result = await db["telemetry"].insert_one(reading.model_dump())
    log.info(f"Telemetry stored for {reading.machine_id} — temp: {reading.temperature}°C")

    return {"message": "Reading stored", "id": str(result.inserted_id)}


# ------------------------------------------------------------
# GET /telemetry/{machine_id} — Get last N readings
# ------------------------------------------------------------
@router.get("/{machine_id}")
async def get_telemetry(
    machine_id: str,
    limit: int = Query(default=50, le=500)   # Default 50, max 500
):
    """
    Fetch the last N telemetry readings for a machine.
    Example: GET /telemetry/CNC-001?limit=100
    """
    db = get_db()
    readings = []

    cursor = db["telemetry"].find(
        {"machine_id": machine_id}
    ).sort("timestamp", -1).limit(limit)    # -1 = newest first

    async for doc in cursor:
        readings.append(format_reading(doc))

    log.info(f"Fetched {len(readings)} readings for {machine_id}")
    return readings


# ------------------------------------------------------------
# GET /telemetry/{machine_id}/latest — Get the most recent reading
# ------------------------------------------------------------
@router.get("/{machine_id}/latest")
async def get_latest_telemetry(machine_id: str):
    """
    Returns just the single most recent reading.
    Used by the dashboard to show current machine state.
    """
    db = get_db()

    doc = await db["telemetry"].find_one(
        {"machine_id": machine_id},
        sort=[("timestamp", -1)]            # Get the newest one
    )

    if not doc:
        raise HTTPException(status_code=404, detail="No telemetry found for this machine")

    return format_reading(doc)
