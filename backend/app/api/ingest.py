"""Document ingestion endpoints."""
import logging
import uuid
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from typing import List
import json
from app.models import IngestBatchRequest
from app.services.task_queue import task_queue_service
from app.security import verify_api_key

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/batch")
async def ingest_batch(
    files: List[UploadFile] = File(...),
    api_key: str = Depends(verify_api_key),
):
    """Ingest batch of documents."""
    try:
        results = []
        
        for file in files:
            content = await file.read()
            
            # Parse based on file type
            if file.filename.endswith('.txt'):
                text_content = content.decode('utf-8')
            elif file.filename.endswith('.json'):
                text_content = json.dumps(json.loads(content.decode('utf-8')))
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
            
            # Enqueue task
            await task_queue_service.enqueue("ingest", task_id, payload)
            
            results.append({
                "filename": file.filename,
                "task_id": task_id,
                "status": "queued",
            })
            
            logger.info(f"Queued ingest task {task_id} for {file.filename}")
        
        return {
            "total_files": len(files),
            "queued": len(results),
            "results": results,
        }
    
    except Exception as e:
        logger.error(f"Failed to ingest batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_ingest_status(task_id: str):
    """Get ingest task status."""
    try:
        status = task_queue_service.get_task_status(task_id)
        return status
    except Exception as e:
        logger.error(f"Failed to get ingest status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
