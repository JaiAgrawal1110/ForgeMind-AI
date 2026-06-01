# ============================================================
# telemetry.py — Defines what a sensor reading looks like
# Telemetry = data sent FROM machines TO our server
# e.g. temperature, spindle speed, machine state
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TelemetryReading(BaseModel):
    """
    One snapshot of sensor data from a machine.
    Machines send this every 2 seconds via WebSocket or Kafka.
    """
    machine_id: str                          # Which machine sent this
    temperature: float                       # In Celsius e.g. 72.4
    spindle_speed: float                     # RPM e.g. 1500.0
    vibration: Optional[float] = None       # Optional sensor
    power_consumption: Optional[float] = None  # In watts, optional
    machine_state: str = "running"          # running / idle / fault
    timestamp: datetime = Field(
        default_factory=datetime.utcnow     # Auto timestamp
    )

class TelemetryResponse(BaseModel):
    """
    What we send back after storing a telemetry reading.
    Includes the DB id so client can reference it later.
    """
    id: str
    machine_id: str
    temperature: float
    spindle_speed: float
    vibration: Optional[float] = None
    power_consumption: Optional[float] = None
    machine_state: str
    timestamp: datetime

# Normal operating ranges (used in anomaly detection later)
# Temperature: 60 - 80°C   → above 90°C = danger
# Spindle speed: 1000-3000 RPM → outside = suspicious
# These are just reference comments — logic lives in ml/
