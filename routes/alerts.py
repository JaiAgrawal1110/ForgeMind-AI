# ============================================================
# alerts.py — Endpoints for viewing and managing alerts
# Base URL: /alerts
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
# GET /alerts
# ------------------------------------------------------------
@router.get("/")
async def get_alerts(
    severity: Optional[str] = Query(None),
    resolved: Optional[bool] = Query(None),
    limit: int = Query(default=50, le=200)
):
    db = get_db()

    query = {}

    if severity:
        query["severity"] = severity

    if resolved is not None:
        query["resolved"] = resolved

    alerts = []

    cursor = (
        db["alerts"]
        .find(query)
        .sort("created_at", -1)
        .limit(limit)
    )

    async for doc in cursor:
        alerts.append(format_alert(doc))

    return alerts


# ------------------------------------------------------------
# POST /alerts
# ------------------------------------------------------------
@router.post("/")
async def create_alert(alert: Alert):
    db = get_db()

    result = await db["alerts"].insert_one(
        alert.model_dump()
    )

    log.warning(
        f"Alert created — machine: {alert.machine_id}"
    )

    return {
        "message": "Alert created",
        "id": str(result.inserted_id)
    }


# ------------------------------------------------------------
# PUT /alerts/{alert_id}/resolve
# ------------------------------------------------------------
@router.put("/{alert_id}/resolve")
async def resolve_alert(alert_id: str):

    db = get_db()

    result = await db["alerts"].update_one(
        {"_id": ObjectId(alert_id)},
        {
            "$set": {
                "resolved": True
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    log.info(f"Alert resolved: {alert_id}")

    return {
        "message": "Alert resolved"
    }


# ------------------------------------------------------------
# GET /alerts/machine/{machine_id}
# ------------------------------------------------------------
@router.get("/machine/{machine_id}")
async def get_machine_alerts(
    machine_id: str,
    resolved: Optional[bool] = Query(None)
):
    db = get_db()

    query = {
        "machine_id": machine_id
    }

    if resolved is not None:
        query["resolved"] = resolved

    alerts = []

    cursor = (
        db["alerts"]
        .find(query)
        .sort("created_at", -1)
    )

    async for doc in cursor:
        alerts.append(format_alert(doc))

    return alerts