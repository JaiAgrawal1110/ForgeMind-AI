# ============================================================
# test_machines.py — Tests for the machines API endpoints
# Run with: pytest tests/
# ============================================================

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from app.main import app

client = TestClient(app)

# ------------------------------------------------------------
# Test: Health check
# ------------------------------------------------------------
def test_root():
    """App should return running status."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


# ------------------------------------------------------------
# Test: Get all machines
# ------------------------------------------------------------
@patch("routes.machines.get_db")
def test_get_all_machines(mock_get_db):
    """Should return list of machines from MongoDB."""
    # Mock MongoDB response
    mock_db = MagicMock()
    mock_db["machines"].find.return_value = AsyncMock(
        __aiter__=AsyncMock(return_value=iter([
            {"_id": "id1", "machine_id": "CNC-001", "name": "Lathe", "location": "Floor A", "status": "active", "created_at": "2026-01-01"}
        ]))
    )
    mock_get_db.return_value = mock_db

    response = client.get("/machines/")
    assert response.status_code == 200


# ------------------------------------------------------------
# Test: Machine not found
# ------------------------------------------------------------
@patch("routes.machines.get_db")
@patch("routes.machines.get_cache")
def test_get_machine_not_found(mock_cache, mock_get_db):
    """Should return 404 when machine doesn't exist."""
    mock_db = MagicMock()
    mock_db["machines"].find_one = AsyncMock(return_value=None)
    mock_get_db.return_value = mock_db

    mock_cache_instance = AsyncMock()
    mock_cache_instance.get = AsyncMock(return_value=None)
    mock_cache.return_value = mock_cache_instance

    response = client.get("/machines/NONEXISTENT")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
