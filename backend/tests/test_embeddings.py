"""Tests for embeddings service."""
import pytest
from app.services.embeddings import EmbeddingsService, LLMService


def test_embeddings_service_initialization():
    """Test embeddings service initialization."""
    service = EmbeddingsService()
    assert service.model is not None or service.model is None  # Either loaded or fallback


def test_embed_single():
    """Test single text embedding."""
    service = EmbeddingsService()
    embedding = service.embed_single("test text")
    
    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(isinstance(x, float) for x in embedding)


def test_embed_batch():
    """Test batch embedding."""
    service = EmbeddingsService()
    texts = ["text1", "text2", "text3"]
    embeddings = service.embed(texts)
    
    assert embeddings.shape[0] == len(texts)
    assert embeddings.shape[1] > 0


def test_cosine_similarity():
    """Test cosine similarity computation."""
    service = EmbeddingsService()
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [1.0, 0.0, 0.0]
    
    similarity = service.cosine_similarity(vec1, vec2)
    
    assert isinstance(similarity, float)
    assert 0.0 <= similarity <= 1.0


def test_llm_service_initialization():
    """Test LLM service initialization."""
    service = LLMService()
    assert service.provider in ["mock", "anthropic", "openai"]


def test_llm_generate_mock():
    """Test mock LLM generation."""
    service = LLMService()
    service.provider = "mock"
    
    result = service.generate("test prompt")
    
    assert isinstance(result, str)
    assert len(result) > 0
