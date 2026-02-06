"""Worker processor for document ingestion."""
import logging
import json
import asyncio
import os
from typing import Dict, Any
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.embeddings import embeddings_service
from app.services.ingest import ingest_document
from app.db import SessionLocal
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents with embedding and validation."""
    
    def __init__(self):
        """Initialize processor."""
        self.embeddings_service = embeddings_service
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def process_document(self, doc_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process single document:
        1. Extract metadata
        2. Compute embedding
        3. Validate numeric fields if present
        4. Store in database
        """
        try:
            title = doc_payload.get("title", "Unknown")
            content = doc_payload.get("content", "")
            metadata = doc_payload.get("metadata", {})
            
            logger.info(f"Processing document: {title}")
            
            # Validate numeric fields if present (self-check)
            numeric_fields = self._extract_numeric_fields(content)
            validation_result = self._validate_numeric_fields(numeric_fields)
            
            if not validation_result["valid"]:
                logger.warning(f"Document {title} failed validation: {validation_result['errors']}")
            
            # Ingest document
            result = await ingest_document(doc_payload)
            
            logger.info(f"Processed document: {title} -> {result}")
            return result
        
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            raise
    
    def _extract_numeric_fields(self, content: str) -> Dict[str, float]:
        """Extract numeric fields from content."""
        # Simple regex-based extraction
        import re
        fields = {}
        
        patterns = {
            "total": r"total[:\s]+(\d+\.?\d*)",
            "sum": r"sum[:\s]+(\d+\.?\d*)",
            "amount": r"amount[:\s]+(\d+\.?\d*)",
            "count": r"count[:\s]+(\d+\.?\d*)",
        }
        
        for field_name, pattern in patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                fields[field_name] = float(matches[0])
        
        return fields
    
    def _validate_numeric_fields(self, fields: Dict[str, float]) -> Dict[str, Any]:
        """Validate numeric fields consistency."""
        # TODO: Implement proper validation logic
        # For now, just check that fields are positive
        errors = []
        for field_name, value in fields.items():
            if value < 0:
                errors.append(f"{field_name} is negative: {value}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }


async def process_batch(documents: list) -> Dict[str, Any]:
    """Process batch of documents in parallel."""
    processor = DocumentProcessor()
    tasks = [
        processor.process_document(doc)
        for doc in documents
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") == "success")
    failed = len(results) - successful
    
    return {
        "total": len(documents),
        "successful": successful,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    # Test processor
    test_doc = {
        "title": "Test Document",
        "content": "Total: 1000, Sum: 500, Amount: 1500, Count: 3",
        "metadata": {"source": "test", "department": "finance"},
    }
    
    processor = DocumentProcessor()
    result = asyncio.run(processor.process_document(test_doc))
    print(f"Result: {result}")
