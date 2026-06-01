# ============================================================
# alerts.py — Endpoints for viewing and managing alerts
# Base URL: /alerts
#
# GET  /alerts                   → list all alerts (with filters)
# POST /alerts                   → create an alert manually
# PUT  /alerts/{id}/resolve      → mark alert as resolved
# GET  /alerts/{machine_id}      → alerts for one machine
# ============================================================

from fastapi import APIRouter, HTTPException, Query
from models.alert import Alert, AlertResponse
from app.database import get_db
from app.logger import log
from typing import Optional
from bson import ObjectId

router = APIRouter()

def format_alert(doc) -> dict:
    doc["id"] = str(doc["_id"])
    del doc["_id"]
    return doc


# ------------------------------------------------------------
# GET /alerts — List alerts with optional filters
# ------------------------------------------------------------
@router.get("/")
async def get_alerts(
    severity: Optional[str] = Query(None),       # Filter by severity
    resolved: Optional[bool] = Query(None),      # Filter by resolved status
    limit: int = Query(default=50, le=200)
):
    """
    Fetch alerts with optional filters.
    Examples:
    GET /alerts                          → all alerts
    GET /alerts?severity=critical        → only critical alerts
    GET /alerts?resolved=false           → only open alerts
    GET /alerts?severity=high&resolved=false
    """
    db = get_db()

    # Build filter query dynamically based on what was passed
    query = {}
    if severity:
        query["severity"] = severity
    if resolved is not None:
        query["resolved"] = resolved

    alerts = []
    cursor = db["alerts"].find(query).sort("created_at", -1).limit(limit)
    async for doc in cursor:
        alerts.append(format_alert(doc))

    return alerts


# ------------------------------------------------------------
# POST /alerts — Create an alert (also called internally by AI)
# ------------------------------------------------------------
@router.post("/")
async def create_alert(alert: Alert):
    """
    Manually create an alert. In production this is called by:
    - The threshold checker (rule-based alerts)
    - The AI anomaly detector (ML-based alerts)
    """
    db = get_db()
    result = await db["alerts"].insert_one(alert.model_dump())
    log.warning(f"Alert created — machine: {alert.machine_id} | severity: {alert.severity} | {alert.message}")
    return {"message": "Alert created", "id": str(result.inserted_id)}


# ------------------------------------------------------------
# PUT /alerts/{alert_id}/resolve — Mark alert as resolved
# ------------------------------------------------------------
@router.put("/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """
    Mark an alert as resolved (someone looked at it and fixed it).
    The red badge on the dashboard disappears when resolved=True.
    """
    db = get_db()

    result = await db["alerts"].update_one(
        {"_id": ObjectId(alert_id)},
        {"$set": {"resolved": True}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")

    log.info(f"Alert resolved: {alert_id}")
    return {"message": "Alert resolved"}


# ------------------------------------------------------------
# GET /alerts/machine/{machine_id} — Alerts for one machine
# ------------------------------------------------------------
@router.get("/machine/{machine_id}")
async def get_machine_alerts(machine_id: str, resolved: Optional[bool] = Query(None)):
    """
    Get all alerts for a specific machine.
    Example: GET /alerts/machine/CNC-001?resolved=false
    """
    db = get_db()
    query = {"machine_id": machine_id}
    if resolved is not None:
        query["resolved"] = resolved

    alerts = []
    async for doc in db["alerts"].find(query).sort("created_at", -1):
        alerts.append(format_alert(doc))

    return alerts
