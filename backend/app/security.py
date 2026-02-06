"""Security utilities."""
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key."""
    if not api_key:
        raise HTTPException(status_code=403, detail="Missing API key")
    
    if api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return api_key


def redact_pii(text: str) -> str:
    """Redact PII from text (stub)."""
    # TODO: Implement proper PII redaction
    # For now, just a placeholder
    return text
