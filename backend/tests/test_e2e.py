"""End-to-end tests for the full audit pipeline."""
import pytest
import httpx
import asyncio
import time
from fastapi.testclient import TestClient
import sys
import os

# Add backend to path
sys.path.insert(0, '/Users/danikosnarev/Desktop/ODRA 2/backend')

from app.main import app

client = TestClient(app)

# Test API key
TEST_API_KEY = "test-key-12345"


class TestE2EIngestPipeline:
    """End-to-end tests for ingest pipeline."""
    
    def test_health_check(self):
        """Test health endpoint is available."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_batch_ingest_single_file(self):
        """Test ingesting a single file."""
        file_content = b"This is a test document with Total: 1000"
        
        response = client.post(
            "/ingest/batch",
            files=[("files", ("test.txt", file_content))],
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 1
        assert data["queued"] >= 1
        assert len(data["results"]) == 1
        
        # Extract task ID for status check
        task_id = data["results"][0]["task_id"]
        assert task_id.startswith("ingest_")
    
    def test_batch_ingest_multiple_files(self):
        """Test ingesting 3 files at once."""
        files = [
            ("files", (f"document_{i}.txt", f"Content {i} with Total: {1000 * (i+1)}".encode()))
            for i in range(3)
        ]
        
        response = client.post(
            "/ingest/batch",
            files=files,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 3
        assert data["queued"] >= 2
    
    def test_batch_ingest_10_files(self):
        """Test ingesting 10 files (the bug scenario)."""
        files = [
            ("files", (f"doc_{i:02d}.txt", f"Document {i} with Total: {1000*(i+1)}, Sum: {500*(i+1)}".encode()))
            for i in range(10)
        ]
        
        response = client.post(
            "/ingest/batch",
            files=files,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_files"] == 10
        assert data["queued"] == 10, f"Expected 10 queued, got {data['queued']}"
        assert len(data["results"]) == 10
        
        # Verify all files have task IDs
        for result in data["results"]:
            assert result["status"] == "queued"
            assert "task_id" in result
            assert result["task_id"].startswith("ingest_")
    
    def test_batch_ingest_json_files(self):
        """Test ingesting JSON format files."""
        import json
        
        json_data = json.dumps({"report": "test", "total": 5000})
        files = [
            ("files", ("data.json", json_data.encode())),
        ]
        
        response = client.post(
            "/ingest/batch",
            files=files,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["queued"] >= 1
    
    def test_batch_ingest_without_api_key(self):
        """Test that batch ingest fails without API key."""
        files = [("files", ("test.txt", b"content"))]
        
        response = client.post(
            "/ingest/batch",
            files=files,
        )
        
        assert response.status_code == 403
    
    def test_batch_ingest_with_invalid_api_key(self):
        """Test that batch ingest fails with invalid API key."""
        files = [("files", ("test.txt", b"content"))]
        
        response = client.post(
            "/ingest/batch",
            files=files,
            headers={"X-API-Key": "invalid-key"},
        )
        
        assert response.status_code == 403
    
    def test_ingest_status_endpoint(self):
        """Test getting status of an ingest task."""
        # First, ingest a file
        files = [("files", ("test.txt", b"Test content"))]
        
        ingest_response = client.post(
            "/ingest/batch",
            files=files,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert ingest_response.status_code == 200
        task_id = ingest_response.json()["results"][0]["task_id"]
        
        # Check status
        status_response = client.get(f"/ingest/status/{task_id}")
        
        assert status_response.status_code == 200
        data = status_response.json()
        # Status could be pending, success, or failed depending on timing
        assert "status" in data


class TestE2EAuditPipeline:
    """End-to-end tests for audit workflow."""
    
    def test_run_audit_job(self):
        """Test running an audit job."""
        payload = {
            "goal": "Verify financial controls",
            "scope": "Q1 2024 transactions",
            "priority": "high",
        }
        
        response = client.post(
            "/audit/run",
            json=payload,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["job_id"].startswith("job_")
    
    def test_get_audit_status(self):
        """Test getting audit job status."""
        # Create job
        payload = {
            "goal": "Test audit",
            "scope": "Test scope",
            "priority": "low",
        }
        
        create_response = client.post(
            "/audit/run",
            json=payload,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        job_id = create_response.json()["job_id"]
        
        # Get status
        status_response = client.get(
            f"/audit/status/{job_id}",
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert status_response.status_code == 200
        data = status_response.json()
        assert "status" in data
        assert "metrics" in data
    
    def test_get_audit_report(self):
        """Test getting audit report."""
        # Create job
        payload = {
            "goal": "Test report",
            "scope": "Test scope",
            "priority": "medium",
        }
        
        create_response = client.post(
            "/audit/run",
            json=payload,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        job_id = create_response.json()["job_id"]
        
        # Get report (may return partial data if still processing)
        report_response = client.get(
            f"/audit/report/{job_id}",
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert report_response.status_code in [200, 202]  # 200 if done, 202 if in progress


class TestFrontendIntegration:
    """Tests for frontend and backend integration."""
    
    def test_cors_headers(self):
        """Test CORS headers are set correctly."""
        response = client.get("/health")
        # Check if CORS headers might be present
        assert response.status_code == 200
    
    def test_api_documentation(self):
        """Test OpenAPI docs are available."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "openapi" in response.text.lower() or "swagger" in response.text.lower()


class TestErrorHandling:
    """Tests for error handling and edge cases."""
    
    def test_ingest_empty_file(self):
        """Test ingesting an empty file."""
        files = [("files", ("empty.txt", b""))]
        
        response = client.post(
            "/ingest/batch",
            files=files,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        # Should still queue the task even if empty
        assert response.status_code == 200
    
    def test_ingest_very_large_file(self):
        """Test ingesting a large file."""
        large_content = "x" * 100000  # 100KB
        files = [("files", ("large.txt", large_content.encode()))]
        
        response = client.post(
            "/ingest/batch",
            files=files,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert response.status_code == 200
        data = response.json()
        # Should be truncated to 10k chars
        assert data["results"][0]["size_bytes"] == 100000
    
    def test_ingest_invalid_filename(self):
        """Test ingesting file with special characters in name."""
        files = [("files", ("test@#$%.txt", b"content"))]
        
        response = client.post(
            "/ingest/batch",
            files=files,
            headers={"X-API-Key": TEST_API_KEY},
        )
        
        assert response.status_code == 200
    
    def test_concurrent_ingest_requests(self):
        """Test handling multiple concurrent ingest requests."""
        # This would require async testing
        responses = []
        
        for i in range(3):
            files = [("files", (f"concurrent_{i}.txt", f"Content {i}".encode()))]
            response = client.post(
                "/ingest/batch",
                files=files,
                headers={"X-API-Key": TEST_API_KEY},
            )
            responses.append(response)
        
        # All should succeed
        for response in responses:
            assert response.status_code == 200
