"""Configuration and environment variables."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables."""
    
    # API
    API_KEY: str = "dev-key-change-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Database
    DATABASE_URL: str = "sqlite:///./odra.db"
    CLICKHOUSE_HOST: str = "localhost"
    CLICKHOUSE_PORT: int = 9000
    CLICKHOUSE_DB: str = "odra"
    USE_CLICKHOUSE: bool = False  # Fallback to SQLite by default
    
    # Redis/Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    USE_CELERY: bool = False  # Fallback to in-process by default
    
    # Embeddings
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # LLM
    LLM_PROVIDER: str = "mock"  # mock, anthropic, openai, google
    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""
    
    # Processing
    MAX_WORKERS: int = 4
    CHUNK_SIZE: int = 1000
    OVERLAP: int = 100
    
    # Audit
    TARGET_PRECISION: float = 0.85
    MAX_ITERATIONS: int = 5
    PRECISION_WEIGHT: float = 0.7
    RECALL_WEIGHT: float = 0.2
    COST_WEIGHT: float = 0.1
    
    class Config:
        env_file = ".env"


settings = Settings()
