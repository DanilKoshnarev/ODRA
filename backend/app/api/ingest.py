"""Document ingestion endpoints."""
import logging
import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from app.services.task_queue import task_queue_service
from app.security import verify_api_key
import redis
import os

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Redis for queue
redis_client: Optional[redis.Redis] = None
try:
    redis_client = redis.from_url(
        os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        decode_responses=True
    )
    if redis_client is not None:
        redis_client.ping()
        logger.info("✅ Redis connected for ingest queue")
except Exception as e:
    logger.warning(f"⚠️ Redis not available: {e}")
    redis_client = None


@router.post("/batch")
async def ingest_batch(
    files: List[UploadFile] = File(...),
    api_key: str = Depends(verify_api_key),
):
    """Ingest batch of documents (up to 10+ files)."""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        logger.info(f"📥 Received {len(files)} files for ingestion")
        
        results = []
        queued_count = 0
        
        for file in files:
            if not file.filename:
                continue
            
            try:
                content = await file.read()
                
                # Parse based on file type
                if file.filename.endswith('.txt'):
                    text_content = content.decode('utf-8')
                elif file.filename.endswith('.json'):
                    try:
                        text_content = json.dumps(json.loads(content.decode('utf-8')))
                    except json.JSONDecodeError:
                        text_content = content.decode('utf-8', errors='ignore')
                else:
                    text_content = content.decode('utf-8', errors='ignore')
                
                # Create ingest task
                task_id = f"ingest_{uuid.uuid4().hex[:12]}"
                
                payload = {
                    "title": file.filename,
                    "content": text_content[:10000],  # Limit to 10k chars
                    "metadata": {
                        "source": "batch_upload",
                        "filename": file.filename,
                        "size": len(content),
                    }
                }
                
                # Queue task in Redis or fallback to in-memory queue
                if redis_client:
                    try:
                        task_json = json.dumps({
                            "task_id": task_id,
                            "payload": payload,
                        })
                        redis_client.rpush("ingest_tasks", task_json)
                        logger.info(f"✅ Queued Redis task {task_id} for {file.filename}")
                    except Exception as e:
                        logger.error(f"Failed to queue in Redis: {e}. Using fallback.")
                        await task_queue_service.enqueue("ingest", task_id, payload)
                else:
                    await task_queue_service.enqueue("ingest", task_id, payload)
                
                results.append({
                    "filename": file.filename,
                    "task_id": task_id,
                    "status": "queued",
                    "size_bytes": len(content),
                })
                queued_count += 1
                
            except Exception as e:
                logger.error(f"Failed to queue file {file.filename}: {e}")
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e),
                })
        
        if queued_count == 0:
            raise HTTPException(status_code=500, detail="Failed to queue any files")
        
        return {
            "total_files": len(files),
            "queued": queued_count,
            "results": results,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest batch: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_ingest_status(task_id: str):
    """Get ingest task status."""
    try:
        # Check Redis first
        if redis_client:
            result_key = f"task_result:{task_id}"
            result_json = redis_client.get(result_key)
            if result_json and isinstance(result_json, str):
                return json.loads(result_json)
        
        # Fallback to in-memory queue
        status = task_queue_service.get_task_status(task_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get ingest status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
