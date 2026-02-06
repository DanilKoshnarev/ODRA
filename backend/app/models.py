"""Pydantic models for request/response schemas."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AuditRunRequest(BaseModel):
    """Request to start an audit job."""
    goal: str = Field(..., description="Audit goal, e.g. 'Find suspicious purchases 2024'")
    scope: Optional[str] = Field(None, description="Scope filter (e.g., department)")
    priority: int = Field(default=5, description="Priority level 1-10")


class AuditJobResponse(BaseModel):
    """Response with job ID."""
    job_id: str
    status: JobStatus
    created_at: datetime


class AuditStatusResponse(BaseModel):
    """Audit job status."""
    job_id: str
    status: JobStatus
    progress_percent: int
    total_documents: int
    processed_documents: int
    metrics: Dict[str, float]
    current_iteration: int


class EvidenceItem(BaseModel):
    """Evidence from document."""
    doc_id: str
    snippet: str
    relevance_score: float
    metadata: Dict[str, Any]


class AuditReport(BaseModel):
    """Final audit report."""
    job_id: str
    goal: str
    status: JobStatus
    total_evidence: int
    precision: float
    recall: float
    evidence: List[EvidenceItem]
    summary: str
    recommendations: List[str]
    generated_at: datetime


class FeedbackRequest(BaseModel):
    """Human feedback for evidence."""
    job_id: str
    doc_id: str
    feedback: str  # "relevant", "irrelevant", "needs_review"
    comment: Optional[str] = None


class DocumentMetadata(BaseModel):
    """Metadata for document."""
    title: str
    source: str
    uploaded_at: datetime
    author: Optional[str] = None
    department: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class IngestBatchRequest(BaseModel):
    """Request to ingest batch of documents."""
    metadata: DocumentMetadata


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    database: str
    embeddings: str
    task_queue: str
    timestamp: datetime
