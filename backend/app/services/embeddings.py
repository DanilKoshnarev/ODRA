"""Embeddings service with LLM abstraction."""
import logging
import numpy as np
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Service for computing embeddings - using mock for fast testing."""
    
    def __init__(self):
        """Initialize embeddings service."""
        self.model = None
        logger.info(f"Using mock embeddings (dimension={settings.EMBEDDING_DIMENSION})")
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Compute embeddings for texts - returns mock embeddings."""
        # For MVP testing, use deterministic mock embeddings based on text hash
        embeddings = []
        for text in texts:
            # Create deterministic embedding based on text
            hash_val = hash(text) % 10000
            np.random.seed(hash_val)
            embedding = np.random.randn(settings.EMBEDDING_DIMENSION).astype(np.float32)
            embeddings.append(embedding)
        
        return np.array(embeddings, dtype=np.float32)
    
    def embed_single(self, text: str) -> List[float]:
        """Compute embedding for single text."""
        embeddings = self.embed([text])
        return embeddings[0].tolist()
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(v1, v2) / (norm1 * norm2))


class LLMService:
    """Service for LLM calls with provider abstraction."""
    
    def __init__(self):
        """Initialize LLM client."""
        self.provider = settings.LLM_PROVIDER
        self.client = None
        
        if self.provider == "anthropic" and settings.ANTHROPIC_API_KEY:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Initialized Anthropic LLM")
            except Exception as e:
                logger.warning(f"Failed to init Anthropic: {e}, falling back to mock")
                self.provider = "mock"
        
        elif self.provider == "openai" and settings.OPENAI_API_KEY:
            try:
                import openai
                openai.api_key = settings.OPENAI_API_KEY
                self.client = openai
                logger.info("Initialized OpenAI LLM")
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}, falling back to mock")
                self.provider = "mock"
        
        elif self.provider == "google" and settings.GOOGLE_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.client = genai
                logger.info("Initialized Google Gemini LLM")
            except Exception as e:
                logger.warning(f"Failed to init Google Gemini: {e}, falling back to mock")
                self.provider = "mock"
        
        else:
            self.provider = "mock"
            logger.info("Using mock LLM for testing")
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using LLM."""
        try:
            if self.provider == "anthropic" and self.client:
                message = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                return message.content[0].text
            
            elif self.provider == "openai" and self.client:
                response = self.client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
            
            elif self.provider == "google" and self.client:
                model = self.client.GenerativeModel("gemini-pro")
                response = model.generate_content(prompt)
                return response.text
            
            else:
                # Mock LLM for testing
                return self._generate_mock_response(prompt)
        
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate mock LLM response for testing."""
        # Extract audit goal from prompt
        if "goal:" in prompt.lower():
            goal_start = prompt.lower().find("goal:") + 5
            goal_end = prompt.find('"', goal_start + 1)
            goal = prompt[goal_start:goal_end].strip()
        else:
            goal = "audit findings"
        
        return f"""## Audit Report Summary

Based on analysis of the provided evidence, here are the key findings:

### Executive Summary
The audit identified critical patterns in the {goal} area. The evidence suggests systematic issues requiring immediate attention.

### Key Findings
1. **High-Risk Items**: Multiple documents show elevated risk indicators
2. **Pattern Recognition**: Consistent anomalies detected across related records
3. **Trend Analysis**: Issues appear concentrated in specific areas

### Recommendations
1. Implement enhanced monitoring for identified risk areas
2. Review control procedures in flagged departments
3. Conduct follow-up audit in 30 days
4. Document all findings for compliance records

---
*Generated by ODRA Mock LLM for MVP Testing*
"""


embeddings_service = EmbeddingsService()
llm_service = LLMService()
