# ============================================================
# test_alerts.py — Tests for the alerts API endpoints
# Run with: pytest tests/
# ============================================================

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app

client = TestClient(app)

# ------------------------------------------------------------
# Test: Get alerts (empty)
# ------------------------------------------------------------
@patch("routes.alerts.get_db")
def test_get_alerts_empty(mock_get_db):
    """Should return empty list when no alerts exist."""
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.__aiter__ = AsyncMock(return_value=iter([]))
    mock_db["alerts"].find.return_value = mock_cursor
    mock_get_db.return_value = mock_db

    response = client.get("/alerts/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ------------------------------------------------------------
# Test: Create alert
# ------------------------------------------------------------
@patch("routes.alerts.get_db")
def test_create_alert(mock_get_db):
    """Should create an alert successfully."""
    mock_db = MagicMock()
    mock_db["alerts"].insert_one = AsyncMock(
        return_value=MagicMock(inserted_id="fake_id")
    )
    mock_get_db.return_value = mock_db

    response = client.post("/alerts/", json={
        "machine_id": "CNC-001",
        "alert_type": "anomaly",
        "severity": "high",
        "message": "Temperature spike detected",
        "anomaly_score": 0.87
    })
    assert response.status_code == 200
    assert "id" in response.json()


# ------------------------------------------------------------
# Test: Severity filter
# ------------------------------------------------------------
@patch("routes.alerts.get_db")
def test_get_alerts_by_severity(mock_get_db):
    """Should filter alerts by severity."""
    mock_db = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.sort.return_value = mock_cursor
    mock_cursor.limit.return_value = mock_cursor
    mock_cursor.__aiter__ = AsyncMock(return_value=iter([]))
    mock_db["alerts"].find.return_value = mock_cursor
    mock_get_db.return_value = mock_db

    response = client.get("/alerts/?severity=critical")
    assert response.status_code == 200
