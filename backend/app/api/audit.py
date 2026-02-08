"""Audit endpoints."""
import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime
from app.models import (
    AuditRunRequest, AuditJobResponse, AuditStatusResponse, 
    AuditReport, EvidenceItem, FeedbackRequest
)
from app.db import SessionLocal, AuditJob, Feedback
from app.services.task_queue import task_queue_service
from app.security import verify_api_key

logger = logging.getLogger(__name__)
router = APIRouter()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/run", response_model=AuditJobResponse)
async def run_audit(
    request: AuditRunRequest,
    api_key: str = Depends(verify_api_key),
    db = Depends(get_db)
):
    """Start a new audit job."""
    try:
        job_id = f"job_{uuid.uuid4().hex[:12]}"
        
        # Create job record
        job = AuditJob(
            id=job_id,
            goal=request.goal,
            scope=request.scope,
            status="pending",  # type: ignore
            progress=0.0,
        )
        db.add(job)
        db.commit()
        
        # Enqueue audit task
        await task_queue_service.enqueue(
            "audit",
            job_id,
            {
                "goal": request.goal,
                "scope": request.scope,
                "priority": request.priority,
            }
        )
        
        logger.info(f"Started audit job {job_id}: {request.goal}")
        
        return AuditJobResponse(
            job_id=job_id,
            status="pending",  # type: ignore
            created_at=datetime.utcnow(),
        )
    
    except Exception as e:
        logger.error(f"Failed to start audit job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{job_id}", response_model=AuditStatusResponse)
async def get_audit_status(job_id: str, db = Depends(get_db)):
    """Get audit job status."""
    try:
        job = db.query(AuditJob).filter(AuditJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return AuditStatusResponse(
            job_id=job_id,
            status=job.status,  # type: ignore
            progress_percent=int(job.progress),
            total_documents=100,  # TODO: Count from database
            processed_documents=int(job.progress),
            metrics={
                "precision": 0.0,
                "recall": 0.0,
                "cost": 0.0,
            },
            current_iteration=0,
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{job_id}", response_model=AuditReport)
async def get_audit_report(job_id: str, db = Depends(get_db)):
    """Get audit report."""
    try:
        job = db.query(AuditJob).filter(AuditJob.id == job_id).first()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        if job.status != "completed":
            raise HTTPException(status_code=202, detail="Job not completed yet")
        
        results = job.results or {}
        
        # Convert evidence to EvidenceItem models
        evidence = [
            EvidenceItem(
                doc_id=e["doc_id"],
                snippet=e["snippet"],
                relevance_score=e["score"],
                metadata=e.get("metadata", {}),
            )
            for e in results.get("evidence", [])
        ]
        
        return AuditReport(
            job_id=job_id,
            goal=job.goal,
            status=job.status,  # type: ignore
            total_evidence=len(evidence),
            precision=results.get("precision", 0.0),
            recall=results.get("recall", 0.0),
            evidence=evidence,
            summary=results.get("summary", ""),
            recommendations=results.get("recommendations", []),
            generated_at=datetime.utcnow(),
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get audit report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback/{job_id}")
async def submit_feedback(
    job_id: str,
    feedback: FeedbackRequest,
    api_key: str = Depends(verify_api_key),
    db = Depends(get_db)
):
    """Submit human feedback for evidence."""
    try:
        feedback_record = Feedback(
            id=f"fb_{uuid.uuid4().hex[:12]}",
            job_id=job_id,
            doc_id=feedback.doc_id,
            feedback_type=feedback.feedback,
            comment=feedback.comment,
        )
        db.add(feedback_record)
        db.commit()
        
        logger.info(f"Recorded feedback for job {job_id}, doc {feedback.doc_id}")
        
        return {
            "status": "recorded",
            "feedback_id": feedback_record.id,
        }
    
    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))
