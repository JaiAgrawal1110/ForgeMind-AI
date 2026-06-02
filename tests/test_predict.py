# ============================================================
# test_predict.py — Tests for the anomaly detection endpoint
# Run with: pytest tests/
# ============================================================

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ------------------------------------------------------------
# Test: Normal reading
# ------------------------------------------------------------
def test_predict_normal():
    """Normal temperature should not trigger anomaly."""
    response = client.post("/predict/", json={
        "machine_id": "CNC-001",
        "temperature": 72.0,        # Normal: 60-80°C
        "spindle_speed": 1800.0,
        "vibration": 0.3,
        "power_consumption": 500.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["anomaly"] == False
    assert data["score"] < 0.5


# ------------------------------------------------------------
# Test: Anomalous reading (overheating)
# ------------------------------------------------------------
def test_predict_anomaly():
    """High temperature should trigger anomaly."""
    response = client.post("/predict/", json={
        "machine_id": "CNC-001",
        "temperature": 120.0,       # Way above normal
        "spindle_speed": 1800.0,
        "vibration": 0.3,
        "power_consumption": 500.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["anomaly"] == True
    assert data["score"] > 0.5


# ------------------------------------------------------------
# Test: Response structure
# ------------------------------------------------------------
def test_predict_response_structure():
    """Response should have required fields."""
    response = client.post("/predict/", json={
        "machine_id": "CNC-TEST",
        "temperature": 75.0,
        "spindle_speed": 2000.0
    })
    assert response.status_code == 200
    data = response.json()
    assert "machine_id" in data
    assert "anomaly" in data
    assert "score" in data
    assert "message" in data
