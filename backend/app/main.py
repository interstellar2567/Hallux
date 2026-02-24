"""
Hallux - AI Hallucination & Citation Verification System
Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import settings
from app.api import verification, health, document
from app.core.cache import cache_service

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> | <level>{message}</level>",
    level=settings.LOG_LEVEL,
)
logger.add(
    settings.LOG_FILE,
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    level=settings.LOG_LEVEL,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Hallux API Server...")
    logger.info(f"📍 Environment: {settings.ENV}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    
    # Initialize Redis cache (optional - gracefully degrades if unavailable)
    try:
        redis_url = settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "redis://localhost:6379/0"
        await cache_service.connect(redis_url)
    except Exception as e:
        logger.warning(f"⚠️ Redis cache disabled (will work without caching): {e}")
    
    yield
    
    logger.info("🛑 Shutting down Hallux API Server...")
    # Cleanup
    try:
        await cache_service.close()
    except Exception as e:
        logger.debug(f"Cache cleanup skipped: {e}")


# Create FastAPI app
app = FastAPI(
    title="Hallux API",
    description="AI Hallucination & Citation Verification System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(verification.router, prefix="/api", tags=["Verification"])
app.include_router(document.router, prefix="/api", tags=["Document Upload"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Hallux API",
        "tagline": "Making AI Trustworthy, One Citation at a Time",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "path": str(request.url),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """General exception handler"""
    logger.exception(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "message": "Internal server error. Please try again later.",
            "path": str(request.url),
        },
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )
