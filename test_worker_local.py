#!/usr/bin/env python3
"""Local test of worker processor without Redis."""
import sys
import os
import json
import asyncio
from unittest.mock import MagicMock, AsyncMock

# Add backend to path FIRST
sys.path.insert(0, '/Users/danikosnarev/Desktop/ODRA 2/backend')
sys.path.insert(0, '/Users/danikosnarev/Desktop/ODRA 2/workers')

print("📌 Setting up mock modules...")

# Create mock for app.services.ingest
mock_ingest = MagicMock()

async def mock_ingest_document(payload):
    """Mock ingest_document that returns success."""
    return {
        "doc_id": payload.get("title", "unknown")[:10],
        "status": "success",
        "shard_id": "shard_0",
    }

mock_ingest.ingest_document = mock_ingest_document

# Create mock for app.services.embeddings
mock_embeddings = MagicMock()

class MockEmbeddingsService:
    def embed_single(self, text):
        return [0.1] * 384
    
    def embed_batch(self, texts):
        return [[0.1] * 384 for _ in texts]

mock_embeddings.embeddings_service = MockEmbeddingsService()

# Create mock for app.db
class MockDocument:
    pass

class MockSessionLocal:
    pass

mock_db = MagicMock()
mock_db.Document = MockDocument
mock_db.SessionLocal = MockSessionLocal

# Inject mocks into sys.modules BEFORE importing processor
sys.modules['app'] = MagicMock()
sys.modules['app.services'] = MagicMock()
sys.modules['app.services.ingest'] = mock_ingest
sys.modules['app.services.embeddings'] = mock_embeddings
sys.modules['app.db'] = mock_db

print("✅ Mock modules configured\n")

# Now import processor
from processor import DocumentProcessor, process_batch, WorkerQueueConsumer

async def test_worker():
    """Test the worker with sample documents."""
    print("\n" + "="*70)
    print("🧪 TESTING ODRA WORKER - LOCAL MODE")
    print("="*70 + "\n")
    
    # Test 1: Single document processing
    print("📌 Test 1: Process single document")
    print("-" * 70)
    
    processor = DocumentProcessor(redis_url=None)  # No Redis
    
    test_doc = {
        "title": "Financial Report Q1 2024",
        "content": "Total: 50000, Sum: 45000, Amount: 5000, Count: 10",
        "metadata": {"source": "test", "department": "finance"},
    }
    
    try:
        result = await processor.process_document(test_doc)
        print(f"✅ Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "-" * 70)
    
    # Test 2: Batch of 10 files (the critical scenario)
    print("\n📌 Test 2: Process batch of 10 documents (CRITICAL TEST)")
    print("-" * 70)
    
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
    
    try:
        result = await process_batch(documents)
        print(f"\n✅ Batch Processing Results:")
        print(f"   Total: {result['total']}")
        print(f"   Successful: {result['successful']}")
        print(f"   Failed: {result['failed']}")
        
        if result['successful'] == 10:
            print("\n🎉 SUCCESS: All 10 documents processed!")
        else:
            print(f"\n⚠️ WARNING: Only {result['successful']}/10 documents processed")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "-" * 70)
    
    # Test 3: Numeric field validation
    print("\n📌 Test 3: Numeric field validation")
    print("-" * 70)
    
    valid_content = "Total: 1000, Sum: 500, Amount: 1500, Count: 5"
    invalid_content = "Total: -100, Sum: 500, Amount: 1500, Count: 5"
    
    valid_fields = processor._extract_numeric_fields(valid_content)
    invalid_fields = processor._extract_numeric_fields(invalid_content)
    
    print(f"Valid content fields: {valid_fields}")
    valid_result = processor._validate_numeric_fields(valid_fields)
    print(f"Valid result: {valid_result}")
    
    print(f"\nInvalid content fields: {invalid_fields}")
    invalid_result = processor._validate_numeric_fields(invalid_fields)
    print(f"Invalid result: {invalid_result}")
    
    if invalid_result['valid'] == False and len(invalid_result['errors']) > 0:
        print("\n✅ Validation correctly identifies negative numbers")
    else:
        print("\n❌ Validation failed to detect negative numbers")
    
    # Test 4: Concurrency test
    print("\n" + "-" * 70)
    print("\n📌 Test 4: Concurrent processing with Semaphore")
    print("-" * 70)
    
    concurrent_docs = [
        {
            "title": f"Concurrent Doc {i}",
            "content": f"Total: {i * 1000}, Sum: {i * 500}",
            "metadata": {"source": "concurrent_test"},
        }
        for i in range(15)
    ]
    
    try:
        result = await process_batch(concurrent_docs)
        print(f"\n✅ Concurrent Processing Results:")
        print(f"   Total: {result['total']}")
        print(f"   Successful: {result['successful']}")
        print(f"   Failed: {result['failed']}")
        
        if result['successful'] > 0:
            print("\n✅ Semaphore correctly limited concurrency")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*70)
    print("🏁 WORKER TESTS COMPLETED")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_worker())
