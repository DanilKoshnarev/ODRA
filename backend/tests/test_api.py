"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

client = TestClient(app)


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    assert "embeddings" in data
    assert "task_queue" in data


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ODRA Backend"
    assert data["status"] == "operational"


def test_audit_run_missing_api_key():
    """Test audit run without API key."""
    response = client.post(
        "/audit/run",
        json={"goal": "Test audit", "priority": 5}
    )
    assert response.status_code == 403


def test_audit_run_invalid_api_key():
    """Test audit run with invalid API key."""
    response = client.post(
        "/audit/run",
        headers={"X-API-Key": "invalid-key"},
        json={"goal": "Test audit", "priority": 5}
    )
    assert response.status_code == 403


def test_audit_run_valid():
    """Test successful audit run."""
    response = client.post(
        "/audit/run",
        headers={"X-API-Key": settings.API_KEY},
        json={"goal": "Test audit", "priority": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"


def test_audit_status():
    """Test getting audit status."""
    # First create a job
    create_response = client.post(
        "/audit/run",
        headers={"X-API-Key": settings.API_KEY},
        json={"goal": "Test audit", "priority": 5}
    )
    job_id = create_response.json()["job_id"]
    
    # Then get status
    response = client.get(
        f"/audit/status/{job_id}",
        headers={"X-API-Key": settings.API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["job_id"] == job_id
    assert "status" in data
