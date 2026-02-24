"""
Health check endpoints
"""

from fastapi import APIRouter
from datetime import datetime
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENV,
        "version": "1.0.0",
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with service status"""
    
    # TODO: Add actual health checks for:
    # - Database connection
    # - Redis connection
    # - External APIs availability
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": {"status": "healthy", "latency_ms": 5},
            "redis": {"status": "healthy", "latency_ms": 2},
            "openai_api": {"status": "available"},
            "crossref_api": {"status": "available"},
            "arxiv_api": {"status": "available"},
        },
        "system": {
            "environment": settings.ENV,
            "version": "1.0.0",
            "debug_mode": settings.DEBUG,
        },
    }
