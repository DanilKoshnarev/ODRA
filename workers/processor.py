"""Worker processor for document ingestion."""
import logging
import json
import asyncio
import os
from typing import Dict, Any, Optional
import sys
import redis

# Ensure Docker-mounted backend is on the Python path.
if os.path.isdir('/app/backend'):
    sys.path.insert(0, '/app/backend')
else:
    sys.path.insert(0, '/app')

from app.services.embeddings import embeddings_service
from app.services.ingest import ingest_document
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents with embedding and validation."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Initialize processor with Redis connection."""
        self.embeddings_service = embeddings_service
        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        
        # Initialize Redis with proper connection pooling
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
            if self.redis_client:
                self.redis_client.ping()
            logger.info("✅ Redis connection established")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}. Using in-memory queue.")
            self.redis_client = None
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
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
            
            logger.info(f"📄 Processing document: {title}")
            
            # Validate numeric fields if present (self-check)
            numeric_fields = self._extract_numeric_fields(content)
            validation_result = self._validate_numeric_fields(numeric_fields)
            
            if not validation_result["valid"]:
                logger.warning(
                    f"⚠️ Document {title} failed validation: {validation_result['errors']}"
                )
            
            # Ingest document
            result = await ingest_document(doc_payload)
            
            logger.info(f"✅ Processed document: {title} -> {result.get('status')}")
            return result
        
        except Exception as e:
            logger.error(f"❌ Failed to process document {title}: {e}", exc_info=True)
            raise
    
    def _extract_numeric_fields(self, content: str) -> Dict[str, float]:
        """Extract numeric fields from content."""
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
                try:
                    fields[field_name] = float(matches[0])
                except (ValueError, IndexError):
                    pass
        
        return fields
    
    def _validate_numeric_fields(self, fields: Dict[str, float]) -> Dict[str, Any]:
        """Validate numeric fields consistency."""
        errors = []
        for field_name, value in fields.items():
            if value < 0:
                errors.append(f"{field_name} is negative: {value}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }


async def process_batch(documents: list) -> Dict[str, Any]:
    """Process batch of documents in parallel with proper concurrency control."""
    processor = DocumentProcessor()
    
    # Process documents with semaphore to avoid overwhelming resources
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent documents
    
    async def process_with_semaphore(doc):
        async with semaphore:
            try:
                return await processor.process_document(doc)
            except Exception as e:
                logger.error(f"Failed to process document: {e}")
                return {"status": "failed", "error": str(e)}
    
    tasks = [process_with_semaphore(doc) for doc in documents]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    
    successful = sum(1 for r in results if isinstance(r, dict) and r.get("status") in ["success", "duplicate"])
    failed = len(results) - successful
    
    logger.info(f"📊 Batch processing complete: {successful}/{len(documents)} successful, {failed} failed")
    
    return {
        "total": len(documents),
        "successful": successful,
        "failed": failed,
        "results": results,
    }


class WorkerQueueConsumer:
    """Consume tasks from Redis queue and process them."""
    
    def __init__(self, queue_name: str = "ingest_tasks"):
        """Initialize queue consumer."""
        self.queue_name = queue_name
        self.processor = DocumentProcessor()
        self.running = False
    
    async def start(self, poll_interval: float = 2.0):
        """Start consuming tasks from queue."""
        if not self.processor.redis_client:
            logger.error("Redis not available. Cannot start queue consumer.")
            return
        
        self.running = True
        logger.info(f"🚀 Starting queue consumer for '{self.queue_name}'")
        
        while self.running:
            try:
                # Pop task from queue (blocking pop with timeout)
                # blpop is synchronous and returns (key, value) tuple or None
                task_data: Optional[tuple] = self.processor.redis_client.blpop(  # type: ignore
                    [self.queue_name],
                    timeout=int(poll_interval)
                )
                
                if task_data is not None:
                    _queue_key, task_json = task_data
                    try:
                        task = json.loads(task_json)  # type: ignore
                        task_id = task.get("task_id", "unknown")
                        payload = task.get("payload", {})
                        
                        logger.info(f"🔄 Processing task {task_id} from queue")
                        
                        # Process document
                        result = await self.processor.process_document(payload)
                        
                        # Store result in Redis
                        result_key = f"task_result:{task_id}"
                        self.processor.redis_client.setex(
                            result_key,
                            3600,  # 1 hour expiry
                            json.dumps(result)
                        )
                        
                        logger.info(f"✅ Task {task_id} completed: {result}")
                    
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in task: {task_json}")
                    except Exception as e:
                        logger.error(f"Error processing task: {e}", exc_info=True)
                else:
                    # No task in queue, continue polling
                    await asyncio.sleep(0.1)
            
            except Exception as e:
                logger.error(f"Queue consumer error: {e}", exc_info=True)
                await asyncio.sleep(5)  # Back off on error
    
    def stop(self):
        """Stop the queue consumer."""
        self.running = False
        logger.info("Stopping queue consumer")


async def main():
    """Main worker entry point."""
    logger.info("🟢 ODRA Worker started")
    
    consumer = WorkerQueueConsumer()
    
    try:
        await consumer.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        consumer.stop()
    except Exception as e:
        logger.error(f"Worker crashed: {e}", exc_info=True)
        consumer.stop()


if __name__ == "__main__":
    # Test processor locally
    test_docs = [
        {
            "title": f"Test Document {i}",
            "content": "Total: 1000, Sum: 500, Amount: 1500, Count: 3",
            "metadata": {"source": "test", "department": "finance"},
        }
        for i in range(10)
    ]
    
    result = asyncio.run(process_batch(test_docs))
    print(json.dumps(result, indent=2))
