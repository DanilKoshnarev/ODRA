"""Auditor service for RAG-based report generation."""
import logging
import json
from typing import Dict, Any, List, Tuple
from datetime import datetime
from app.db import SessionLocal, Document, AuditJob
from app.services.embeddings import embeddings_service, llm_service
from app.config import settings

logger = logging.getLogger(__name__)


class AuditorPlanner:
    """Planner that decomposes audit goal into search queries."""
    
    def __init__(self, goal: str, scope: str = None):
        """Initialize planner."""
        self.goal = goal
        self.scope = scope
        self.iteration = 0
        self.max_iterations = settings.MAX_ITERATIONS
        self.target_precision = settings.TARGET_PRECISION
    
    def decompose_goal(self) -> List[str]:
        """Decompose goal into subqueries."""
        subqueries = [
            self.goal,
            f"verify {self.goal}",
            f"evidence for {self.goal}",
        ]
        return subqueries
    
    async def vector_search(self, query: str, top_k: int = 10) -> List[Tuple[Document, float]]:
        """Search documents using vector similarity."""
        try:
            query_embedding = embeddings_service.embed_single(query)
            db = SessionLocal()
            docs = db.query(Document).limit(100).all()
            
            results = []
            for doc in docs:
                try:
                    doc_embedding = json.loads(doc.embedding)
                    score = embeddings_service.cosine_similarity(query_embedding, doc_embedding)
                    results.append((doc, score))
                except Exception as e:
                    logger.warning(f"Failed to compute similarity for doc {doc.id}: {e}")
            
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
        
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
        finally:
            db.close()
    
    async def run_audit(self, job_id: str) -> Dict[str, Any]:
        """Run audit and generate report."""
        try:
            db = SessionLocal()
            job = db.query(AuditJob).filter(AuditJob.id == job_id).first()
            
            if not job:
                return {"error": "Job not found"}
            
            job.status = "processing"
            db.commit()
            
            subqueries = self.decompose_goal()
            logger.info(f"Decomposed goal into {len(subqueries)} subqueries")
            
            all_evidence = []
            for query in subqueries:
                results = await self.vector_search(query, top_k=5)
                for doc, score in results:
                    all_evidence.append({
                        "doc_id": doc.id,
                        "title": doc.title,
                        "snippet": doc.content[:200],
                        "score": float(score),
                        "metadata": doc.doc_metadata,
                    })
            
            seen = set()
            unique_evidence = []
            for item in all_evidence:
                if item["doc_id"] not in seen:
                    unique_evidence.append(item)
                    seen.add(item["doc_id"])
            
            unique_evidence.sort(key=lambda x: x["score"], reverse=True)
            
            prompt = self._build_synthesis_prompt(self.goal, unique_evidence)
            summary = llm_service.generate(prompt, max_tokens=500)
            
            precision = min(1.0, len(unique_evidence) / max(1, len(unique_evidence)))
            recall = min(1.0, sum(e["score"] for e in unique_evidence[:10]) / 10.0)
            
            recommendations = self._generate_recommendations(summary, unique_evidence)
            
            results = {
                "goal": self.goal,
                "total_evidence": len(unique_evidence),
                "precision": precision,
                "recall": recall,
                "evidence": unique_evidence[:20],
                "summary": summary,
                "recommendations": recommendations,
            }
            
            job.status = "completed"
            job.results = results
            job.progress = 100.0
            db.commit()
            
            logger.info(f"Audit completed: {job_id}")
            return results
        
        except Exception as e:
            logger.error(f"Audit failed: {e}")
            job.status = "failed"
            db.commit()
            return {"error": str(e)}
        finally:
            db.close()
    
    def _build_synthesis_prompt(self, goal: str, evidence: List[Dict]) -> str:
        """Build prompt for LLM synthesis."""
        evidence_text = "\n".join([
            f"- {e['title']}: {e['snippet']} (score: {e['score']:.2f})"
            for e in evidence[:10]
        ])
        
        return f"""Based on the following evidence, provide a concise audit report for the goal: "{goal}"

Evidence:
{evidence_text}

Report should include:
1. Summary of findings
2. Key risks identified
3. Recommended actions

Report:"""
    
    def _generate_recommendations(self, summary: str, evidence: List[Dict]) -> List[str]:
        """Generate recommendations from summary and evidence."""
        return [
            "Review high-score documents for compliance",
            "Implement automated monitoring for similar patterns",
            "Schedule follow-up audit in 30 days",
        ]


async def run_audit_job(job_id: str, goal: str, scope: str = None) -> Dict[str, Any]:
    """Run audit job."""
    planner = AuditorPlanner(goal, scope)
    return await planner.run_audit(job_id)
