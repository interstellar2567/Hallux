"""
Redis Caching Layer for API Responses
Caches Crossref, arXiv, and OpenAlex API calls to avoid rate limits
"""

import json
import hashlib
from typing import Optional, Any
from loguru import logger
import redis.asyncio as aioredis
from functools import wraps

class CacheService:
    """
    Async Redis cache for API responses
    """
    
    def __init__(self):
        self.redis = None
        self.enabled = False
        
    async def connect(self, redis_url: str = "redis://localhost:6379/0"):
        """Connect to Redis server"""
        try:
            self.redis = await aioredis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            await self.redis.ping()
            self.enabled = True
            logger.info(f"✅ Redis cache connected: {redis_url}")
        except Exception as e:
            logger.warning(f"⚠️ Redis cache disabled (connection failed): {e}")
            self.enabled = False
            self.redis = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(value)
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """
        Set value in cache with TTL (time-to-live)
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default 1 hour)
        """
        if not self.enabled:
            return
        
        try:
            await self.redis.set(
                key,
                json.dumps(value),
                ex=ttl
            )
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.enabled:
            return
        
        try:
            await self.redis.delete(key)
            logger.debug(f"Cache DELETE: {key}")
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            try:
                await self.redis.close()
                logger.info("Redis connection closed")
            except Exception as e:
                logger.debug(f"Redis close error: {e}")
    
    def make_key(self, prefix: str, *args) -> str:
        """
        Generate cache key from prefix and arguments
        
        Example:
            make_key("crossref", "10.1038/s41586-020-03051-4")
            -> "crossref:a3f8b9c..."
        """
        # Hash the arguments for consistent keys
        content = ":".join(str(arg) for arg in args)
        hash_suffix = hashlib.md5(content.encode()).hexdigest()[:12]
        return f"{prefix}:{hash_suffix}"


# Global cache instance
cache_service = CacheService()


def cached(prefix: str, ttl: int = 3600):
    """
    Decorator for caching async function results
    
    Usage:
        @cached("crossref", ttl=3600)
        async def verify_doi(doi: str):
            # Expensive API call
            return result
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function args
            key = cache_service.make_key(prefix, *args, *kwargs.values())
            
            # Try to get from cache
            cached_result = await cache_service.get(key)
            if cached_result is not None:
                return cached_result
            
            # Call function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(key, result, ttl=ttl)
            return result
        
        return wrapper
    return decorator
