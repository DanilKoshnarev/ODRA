"""Health check endpoints."""
from fastapi import APIRouter
from datetime import datetime
from app.models import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        database="connected",
        embeddings="ready",
        task_queue="ready",
        timestamp=datetime.utcnow(),
    )
