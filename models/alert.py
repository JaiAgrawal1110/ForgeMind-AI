# ============================================================
# alert.py — Defines what an Alert looks like
# Alert = notification that something went wrong on a machine
# Created when: temp too high, AI detects anomaly, etc.
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Alert(BaseModel):
    """
    An alert is created when a machine behaves abnormally.
    Two ways an alert gets triggered:
    1. Rule-based: temperature > 90°C for 3 consecutive readings
    2. AI-based: Isolation Forest flags anomaly score > threshold
    """
    machine_id: str                          # Which machine triggered this
    alert_type: str                          # "threshold" or "anomaly"
    severity: str                            # "low", "medium", "high", "critical"
    message: str                             # Human readable description
    anomaly_score: Optional[float] = None   # AI confidence score (0.0 - 1.0)
    resolved: bool = False                  # Has someone acknowledged this?
    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

class AlertResponse(BaseModel):
    """What we send back when returning alerts from the DB."""
    id: str
    machine_id: str
    alert_type: str
    severity: str
    message: str
    anomaly_score: Optional[float] = None
    resolved: bool
    created_at: datetime

# Severity guide:
# low      → slightly outside normal range, keep watching
# medium   → consistently abnormal, investigate soon
# high     → immediate attention needed
# critical → machine likely failing, stop it
