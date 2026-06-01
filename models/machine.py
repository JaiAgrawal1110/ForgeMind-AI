# ============================================================
# machine.py — Defines what a "Machine" looks like in our app
# Pydantic models = blueprints for data
# If data doesn't match the blueprint, FastAPI auto-rejects it
# ============================================================

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Machine(BaseModel):
    """
    Represents a physical CNC machine on the factory floor.
    When someone sends a POST /machines request, 
    the data must match this shape exactly.
    """
    machine_id: str                          # Unique ID e.g. "CNC-001"
    name: str                                # Human readable name e.g. "Lathe Machine 1"
    location: str                            # Where it is e.g. "Floor A"
    status: str = "active"                   # Default: active. Can be: active, idle, fault
    created_at: datetime = Field(            # Auto-set to current time
        default_factory=datetime.utcnow
    )

class MachineUpdate(BaseModel):
    """
    Used when updating a machine — all fields optional
    because you might only want to update one field at a time
    """
    name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None

class MachineResponse(BaseModel):
    """
    What we send BACK to the client after creating/fetching a machine.
    Same as Machine but includes the MongoDB _id as a string.
    """
    id: str                                  # MongoDB document ID
    machine_id: str
    name: str
    location: str
    status: str
    created_at: datetime
