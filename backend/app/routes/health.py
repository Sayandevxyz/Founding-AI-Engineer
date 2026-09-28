"""Health and diagnostics endpoints."""
from fastapi import APIRouter
import sys
import os

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
async def health_check():
    return {
        "status": "ok",
        "service": "Replicate.AI Orchestration Engine",
        "version": "1.0.0",
        "python_version": sys.version,
        "playwright_enabled": True,
        "llm_configured": bool(os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")),
        "database": "SQLite/SQLAlchemy"
    }
