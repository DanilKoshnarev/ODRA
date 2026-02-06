"""Embeddings service with LLM abstraction."""
import logging
import numpy as np
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingsService:
    """Service for computing embeddings."""
    
    def __init__(self):
        """Initialize embeddings model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Loaded embeddings model: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load embeddings model: {e}")
            self.model = None
    
    def embed(self, texts: List[str]) -> np.ndarray:
        """Compute embeddings for texts."""
        if not self.model:
            return np.random.randn(len(texts), settings.EMBEDDING_DIMENSION).astype(np.float32)
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.astype(np.float32)
        except Exception as e:
            logger.error(f"Failed to compute embeddings: {e}")
            return np.random.randn(len(texts), settings.EMBEDDING_DIMENSION).astype(np.float32)
    
    def embed_single(self, text: str) -> List[float]:
        """Compute embedding for single text."""
        embeddings = self.embed([text])
        return embeddings[0].tolist()
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


class LLMService:
    """Service for LLM calls with provider abstraction."""
    
    def __init__(self):
        """Initialize LLM client."""
        self.provider = settings.LLM_PROVIDER
        self.client = None
        
        if self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                logger.info("Initialized Anthropic LLM")
            except Exception as e:
                logger.warning(f"Failed to init Anthropic: {e}, falling back to mock")
                self.provider = "mock"
        
        elif self.provider == "openai":
            try:
                import openai
                openai.api_key = settings.OPENAI_API_KEY
                self.client = openai
                logger.info("Initialized OpenAI LLM")
            except Exception as e:
                logger.warning(f"Failed to init OpenAI: {e}, falling back to mock")
                self.provider = "mock"
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using LLM."""
        try:
            if self.provider == "anthropic":
                message = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                return message.content[0].text
            
            elif self.provider == "openai":
                response = self.client.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
            
            else:
                return f"[Mock LLM] Summary based on: {prompt[:100]}..."
        
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return f"[Fallback] Unable to generate report: {str(e)}"


embeddings_service = EmbeddingsService()
llm_service = LLMService()
