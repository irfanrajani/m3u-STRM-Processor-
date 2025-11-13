"""Redis caching utilities."""
import json
import logging
from typing import Optional, Any
from redis import Redis
from app.core.config import settings

logger = logging.getLogger(__name__)

try:
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    redis_client.ping()
    logger.info("Redis connection established successfully")
except Exception as e:
    logger.warning(f"Redis not available: {e}. Caching will be disabled.")
    redis_client = None


class CacheManager:
    """Manage caching operations with Redis."""

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """
        Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if not redis_client:
            return None
        try:
            value = redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error for key '{key}': {e}")
            return None

    @staticmethod
    def set(key: str, value: Any, ttl: int = 300) -> bool:
        """
        Set cached value with TTL in seconds.

        Args:
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time-to-live in seconds (default: 300 = 5 minutes)

        Returns:
            True if successful
        """
        if not redis_client:
            return False
        try:
            redis_client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Cache set error for key '{key}': {e}")
            return False

    @staticmethod
    def delete(key: str) -> bool:
        """
        Delete cached value.

        Args:
            key: Cache key to delete

        Returns:
            True if successful
        """
        if not redis_client:
            return False
        try:
            redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key '{key}': {e}")
            return False

    @staticmethod
    def clear_pattern(pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "cache:channels:*")

        Returns:
            Number of keys deleted
        """
        if not redis_client:
            return 0
        try:
            keys = redis_client.keys(pattern)
            if keys:
                return redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for '{pattern}': {e}")
            return 0

    @staticmethod
    def invalidate_channel_cache():
        """Invalidate all channel-related caches."""
        CacheManager.clear_pattern("cache:channels:*")
        logger.info("Channel cache invalidated")

    @staticmethod
    def invalidate_vod_cache():
        """Invalidate all VOD-related caches."""
        CacheManager.clear_pattern("cache:vod:*")
        logger.info("VOD cache invalidated")

    @staticmethod
    def invalidate_provider_cache(provider_id: Optional[int] = None):
        """Invalidate provider-related caches."""
        if provider_id:
            CacheManager.clear_pattern(f"cache:provider:{provider_id}:*")
        else:
            CacheManager.clear_pattern("cache:provider:*")
        logger.info(f"Provider cache invalidated{f' for provider {provider_id}' if provider_id else ''}")
