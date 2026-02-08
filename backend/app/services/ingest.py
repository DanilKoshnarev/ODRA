"""Document ingestion service."""
import logging
import hashlib
import json
from typing import Dict, Any, List
from datetime import datetime
from app.db import SessionLocal, Document
from app.services.embeddings import embeddings_service
from app.config import settings

logger = logging.getLogger(__name__)


def compute_shard_id(metadata: Dict[str, Any], title_embedding: List[float]) -> str:
    """Compute shard ID from metadata and title embedding."""
    shard_key = f"{metadata.get('source', '')}_{metadata.get('department', '')}"
    shard_hash = hashlib.md5(shard_key.encode()).hexdigest()
    shard_idx = int(shard_hash, 16) % settings.MAX_WORKERS
    return f"shard_{shard_idx}"


def compute_idempotency_key(title: str, source: str) -> str:
    """Compute idempotency key for document."""
    key = f"{title}_{source}_{datetime.utcnow().date()}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


async def ingest_document(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ingest a single document: parse, embed, validate, store."""
    try:
        title = payload.get("title", "Unknown")
        content = payload.get("content", "")
        metadata = payload.get("metadata", {})
        
        idempotency_key = compute_idempotency_key(title, metadata.get("source", ""))
        
        db = SessionLocal()
        existing = db.query(Document).filter(Document.id == idempotency_key).first()
        if existing:
            logger.info(f"Document already exists: {idempotency_key}")
            return {"doc_id": idempotency_key, "status": "duplicate"}
        
        embedding = embeddings_service.embed_single(f"{title} {content[:500]}")
        shard_id = compute_shard_id(metadata, embedding)
        
        doc = Document(
            id=idempotency_key,
            title=title,
            content=content[:5000],
            embedding=json.dumps(embedding),
            doc_metadata={**metadata, "shard_id": shard_id},
            source=metadata.get("source", "unknown"),
        )
        
        db.add(doc)
        db.commit()
        
        logger.info(f"Ingested document: {idempotency_key}")
        
        return {
            "doc_id": idempotency_key,
            "status": "success",
            "shard_id": shard_id,
            "title": title,
        }
    
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}")
        return {"status": "failed", "error": str(e)}
    finally:
        db.close()


async def ingest_batch(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Ingest batch of documents."""
    results = []
    
    for doc_payload in documents:
        result = await ingest_document(doc_payload)
        results.append(result)
    
    successful = sum(1 for r in results if r.get("status") == "success")
    return {
        "total": len(documents),
        "successful": successful,
        "results": results,
    }
