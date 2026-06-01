# ============================================================
# predict.py — AI anomaly detection endpoint
# Base URL: /predict
#
# POST /predict — Send telemetry, get back anomaly verdict
#
# NOTE: This is a placeholder for now (Week 1)
# The actual ML model gets added in Week 5
# For now it returns a dummy response so the app doesn't crash
# ============================================================

from fastapi import APIRouter
from pydantic import BaseModel
from app.logger import log

router = APIRouter()

# Input shape for prediction request
class PredictRequest(BaseModel):
    machine_id: str
    temperature: float
    spindle_speed: float
    vibration: float = 0.0
    power_consumption: float = 0.0


# Output shape
class PredictResponse(BaseModel):
    machine_id: str
    anomaly: bool         # True = something's wrong
    score: float          # 0.0 = normal, 1.0 = definitely anomaly
    message: str


# ------------------------------------------------------------
# POST /predict — Run anomaly detection
# ------------------------------------------------------------
@router.post("/", response_model=PredictResponse)
async def predict_anomaly(data: PredictRequest):
    """
    Send a telemetry snapshot, get back an anomaly verdict.

    Body example:
    {
        "machine_id": "CNC-001",
        "temperature": 95.0,
        "spindle_speed": 1800,
        "vibration": 0.5
    }

    Response:
    {
        "machine_id": "CNC-001",
        "anomaly": true,
        "score": 0.87,
        "message": "Anomaly detected"
    }

    Week 5: Replace the dummy logic below with real Isolation Forest model
    """

    # ----------------------------------------------------------
    # WEEK 5: Replace this block with actual model.predict(data)
    # ----------------------------------------------------------
    # Dummy rule for now: if temp > 90, flag as anomaly
    is_anomaly = data.temperature > 90.0
    score = round((data.temperature - 60) / 40, 2) if is_anomaly else 0.1

    log.info(f"Prediction for {data.machine_id} — anomaly: {is_anomaly}, score: {score}")

    return PredictResponse(
        machine_id=data.machine_id,
        anomaly=is_anomaly,
        score=min(score, 1.0),
        message="Anomaly detected" if is_anomaly else "Normal operation"
    )
