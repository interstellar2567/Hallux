"""
Configuration settings for Hallux API
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    ENV: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    RELOAD: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/hallux"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str = ""
    REDIS_CACHE_TTL: int = 3600
    
    # API Keys
    OPENAI_API_KEY: str = ""
    GOOGLE_API_KEY: str = ""  # Gemini API key
    GEMINI_API_KEY: str = ""  # Alias for GOOGLE_API_KEY
    ANTHROPIC_API_KEY: str = ""
    
    # External APIs
    CROSSREF_EMAIL: str = ""
    SERPER_API_KEY: str = ""
    OPENALEX_EMAIL: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://hallux.vercel.app",
        "https://hallux-*.vercel.app"
    ]
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Verification Settings
    MAX_CITATIONS_PER_REQUEST: int = 100
    VERIFICATION_TIMEOUT_SECONDS: int = 30
    ENABLE_AI_SCORING: bool = True
    ENABLE_CITATION_GRAPH: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/hallux.log"
    
    # Playwright
    PLAYWRIGHT_HEADLESS: bool = True
    PLAYWRIGHT_TIMEOUT: int = 30000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


settings = Settings()
