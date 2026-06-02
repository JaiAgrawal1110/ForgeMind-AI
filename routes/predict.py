from fastapi import APIRouter
from pydantic import BaseModel
from app.logger import log
from ml.anomaly_model import predict, is_model_loaded

router = APIRouter()

class PredictRequest(BaseModel):
    machine_id: str
    temperature: float
    spindle_speed: float
    vibration: float = 0.3
    power_consumption: float = 500.0

class PredictResponse(BaseModel):
    machine_id: str
    anomaly: bool
    score: float
    message: str
    confidence: str = "rule-based"

@router.post("/", response_model=PredictResponse)
async def predict_anomaly(data: PredictRequest):
    is_anomaly, score, confidence = predict(
        temperature=data.temperature,
        spindle_speed=data.spindle_speed,
        vibration=data.vibration,
        power_consumption=data.power_consumption
    )

    log.info(f"Prediction for {data.machine_id} — anomaly: {is_anomaly}, score: {score}")

    return PredictResponse(
        machine_id=data.machine_id,
        anomaly=is_anomaly,
        score=score,
        message="Anomaly detected" if is_anomaly else "Normal operation",
        confidence=confidence
    )