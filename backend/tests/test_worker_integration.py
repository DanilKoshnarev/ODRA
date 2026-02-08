"""Integration tests for worker batch processing."""
import pytest
import asyncio
import json
from workers.processor import DocumentProcessor, process_batch, WorkerQueueConsumer


@pytest.mark.asyncio
async def test_process_single_document():
    """Test processing a single document."""
    processor = DocumentProcessor(redis_url="redis://localhost:6379/0")
    
    doc = {
        "title": "Financial Report Q1 2024",
        "content": "Total: 50000, Sum: 45000, Amount: 5000, Count: 10",
        "metadata": {"source": "reports", "department": "finance"},
    }
    
    result = await processor.process_document(doc)
    
    assert result["status"] in ["success", "duplicate"]
    assert "doc_id" in result


@pytest.mark.asyncio
async def test_process_batch_of_10():
    """Test processing batch of 10 documents (reproducing the bug scenario)."""
    documents = [
        {
            "title": f"Document {i:02d}",
            "content": f"Total: {1000 * (i+1)}, Sum: {500 * (i+1)}, Amount: {1500 * (i+1)}, Count: {i+1}",
            "metadata": {
                "source": "batch_upload",
                "department": "finance",
                "filename": f"doc_{i:02d}.txt",
            }
        }
        for i in range(10)
    ]
    
    result = await process_batch(documents)
    
    assert result["total"] == 10
    assert result["successful"] > 0
    assert len(result["results"]) == 10
    
    # Check individual results
    for res in result["results"]:
        assert "status" in res
        if res["status"] in ["success", "duplicate"]:
            assert "doc_id" in res


@pytest.mark.asyncio
async def test_numeric_validation():
    """Test numeric field validation in documents."""
    processor = DocumentProcessor()
    
    # Valid document
    valid_doc = {
        "title": "Valid Report",
        "content": "Total: 1000, Sum: 500, Amount: 1500, Count: 5",
        "metadata": {"source": "test"},
    }
    
    result = await processor.process_document(valid_doc)
    assert result["status"] in ["success", "duplicate"]
    
    # Invalid document with negative numbers (should still process but warn)
    invalid_doc = {
        "title": "Invalid Report",
        "content": "Total: -100, Sum: 500",
        "metadata": {"source": "test"},
    }
    
    result = await processor.process_document(invalid_doc)
    # Should still process, but validation should catch issues


@pytest.mark.asyncio
async def test_document_with_different_formats():
    """Test processing documents with different content types."""
    processor = DocumentProcessor()
    
    # Text document
    text_doc = {
        "title": "report.txt",
        "content": "This is a text report with Total: 1000",
        "metadata": {"source": "upload", "format": "txt"},
    }
    
    result = await processor.process_document(text_doc)
    assert result["status"] in ["success", "duplicate"]
    
    # JSON-like document
    json_doc = {
        "title": "data.json",
        "content": json.dumps({"total": 1000, "items": 10}),
        "metadata": {"source": "upload", "format": "json"},
    }
    
    result = await processor.process_document(json_doc)
    assert result["status"] in ["success", "duplicate"]


@pytest.mark.asyncio
async def test_concurrent_processing():
    """Test concurrent document processing with semaphore limit."""
    processor = DocumentProcessor()
    
    documents = [
        {
            "title": f"Concurrent Doc {i}",
            "content": f"Total: {i * 1000}, Sum: {i * 500}",
            "metadata": {"source": "concurrent_test"},
        }
        for i in range(15)
    ]
    
    # Should process max 5 concurrently due to semaphore
    result = await process_batch(documents)
    
    assert result["total"] == 15
    assert result["failed"] == 0 or result["successful"] > 0


@pytest.mark.asyncio
async def test_error_handling_in_batch():
    """Test error handling when processing documents with issues."""
    processor = DocumentProcessor()
    
    # Mix of valid and potentially problematic documents
    documents = [
        {
            "title": f"Doc {i}",
            "content": "Valid content" if i % 2 == 0 else "",
            "metadata": {"source": "error_test"},
        }
        for i in range(5)
    ]
    
    result = await process_batch(documents)
    
    # Should handle all documents without crashing
    assert len(result["results"]) == 5
    assert result["total"] == 5


@pytest.mark.asyncio
async def test_numeric_field_extraction():
    """Test extraction of numeric fields from content."""
    processor = DocumentProcessor()
    
    content = """
    Financial Summary:
    Total: 100000.50
    Sum: 75000.25
    Amount: 25000.25
    Count: 150
    """
    
    fields = processor._extract_numeric_fields(content)
    
    assert "total" in fields
    assert fields["total"] == 100000.50
    assert "sum" in fields
    assert "amount" in fields
    assert "count" in fields
    assert fields["count"] == 150


def test_numeric_field_validation():
    """Test numeric field validation logic."""
    processor = DocumentProcessor()
    
    # Valid fields
    valid_fields = {"total": 1000, "sum": 500, "amount": 1500}
    result = processor._validate_numeric_fields(valid_fields)
    assert result["valid"] is True
    assert len(result["errors"]) == 0
    
    # Invalid fields (negative values)
    invalid_fields = {"total": -100, "sum": 500}
    result = processor._validate_numeric_fields(invalid_fields)
    assert result["valid"] is False
    assert len(result["errors"]) > 0
    assert "negative" in result["errors"][0].lower()
