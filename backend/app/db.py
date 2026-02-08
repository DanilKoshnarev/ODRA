"""Database initialization and models."""
import logging
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class Document(Base):
    """Document storage model."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True)
    title = Column(String)
    content = Column(Text)
    embedding = Column(Text)  # JSON serialized list of floats
    doc_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String)


class AuditJob(Base):
    """Audit job tracking model."""
    __tablename__ = "audit_jobs"
    
    id = Column(String, primary_key=True)
    goal = Column(String)
    scope = Column(String, nullable=True)
    status = Column(String, default="pending")
    progress = Column(Float, default=0.0)
    results = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Feedback(Base):
    """Human feedback model."""
    __tablename__ = "feedback"
    
    id = Column(String, primary_key=True)
    job_id = Column(String)
    doc_id = Column(String)
    feedback_type = Column(String)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Initialize database
engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


async def init_db():
    """Initialize database tables."""
    try:
        Base.metadata.create_all(engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
