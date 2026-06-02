"""L2 Redis Cache

Implements Redis distributed cache as the second layer (L2 Cache).
Provides persistent, shared caching across processes/services.
"""

import json
from typing import Any

import redis

from src.core.config import settings


class L2RedisCache:
    """L2 Redis Cache Implementation"""

    def __init__(self):
        """Initialize Redis connection"""
        self._client = None
        self._connect()

    def _connect(self):
        """Establish Redis connection"""
        try:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            self._client.ping()
        except Exception:
            self._client = None

    def _ensure_connection(self):
        """Ensure Redis connection is established"""
        if self._client is None:
            self._connect()
        return self._client

    def get(self, key: str) -> Any | None:
        """Get value by key"""
        client = self._ensure_connection()
        if not client:
            return None

        try:
            value = client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception:
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value with optional TTL"""
        client = self._ensure_connection()
        if not client:
            return

        try:
            value_str = json.dumps(value)
            if ttl:
                client.setex(key, ttl, value_str)
            else:
                client.set(key, value_str)
        except Exception:
            pass

    def delete(self, key: str) -> None:
        """Delete value by key"""
        client = self._ensure_connection()
        if not client:
            return

        try:
            client.delete(key)
        except Exception:
            pass

    def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching pattern"""
        client = self._ensure_connection()
        if not client:
            return

        try:
            keys = client.keys(f"{pattern}*")
            if keys:
                client.delete(*keys)
        except Exception:
            pass

    def clear(self) -> None:
        """Clear all cache entries"""
        client = self._ensure_connection()
        if not client:
            return

        try:
            client.flushdb()
        except Exception:
            pass
