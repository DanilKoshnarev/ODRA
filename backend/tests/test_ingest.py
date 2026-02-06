"""Tests for ingest service."""
import pytest
import asyncio
from app.services.ingest import ingest_document, compute_idempotency_key


@pytest.mark.asyncio
async def test_ingest_document():
    """Test document ingestion."""
    payload = {
        "title": "Test Document",
        "content": "This is test content with Total: 1000",
        "metadata": {"source": "test", "department": "finance"},
    }
    
    result = await ingest_document(payload)
    
    assert result["status"] in ["success", "duplicate"]
    assert "doc_id" in result


@pytest.mark.asyncio
async def test_idempotency():
    """Test idempotency key generation."""
    key1 = compute_idempotency_key("Test", "source1")
    key2 = compute_idempotency_key("Test", "source1")
    key3 = compute_idempotency_key("Test", "source2")
    
    assert key1 == key2
    assert key1 != key3


def test_compute_idempotency_key():
    """Test idempotency key computation."""
    key = compute_idempotency_key("Document Title", "test_source")
    assert len(key) == 16
    assert isinstance(key, str)
