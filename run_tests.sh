#!/bin/bash
set -e

echo "🔧 Installing dependencies..."
pip install -q pytest pytest-asyncio httpx fastapi uvicorn sqlalchemy

echo "✅ Running Backend Unit Tests..."
python3 -m pytest backend/tests/test_ingest.py backend/tests/test_embeddings.py -v --tb=short

echo "✅ Running Worker Integration Tests..."
python3 -m pytest backend/tests/test_worker_integration.py -v --tb=short

echo "✅ Running E2E Tests..."
python3 -m pytest backend/tests/test_e2e.py::TestE2EIngestPipeline::test_batch_ingest_10_files -v --tb=short

echo "🎉 All critical tests passed!"
