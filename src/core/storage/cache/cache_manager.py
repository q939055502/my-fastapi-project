"""Cache Manager

Unified cache manager that encapsulates L1 (local), L2 (Redis), and L3 (database) caches.
Provides a single interface for all cache operations.

Query Flow (Read-Through):
    L1 -> L2 -> L3 (database) -> Update L2 -> Update L1 -> Return

Write Flow (Write-Through):
    Update database -> Delete L1 -> Delete L2
"""

import hashlib
from collections.abc import Callable
from functools import wraps
from typing import Any

from src.core.config import settings

from .l1_local import L1LocalCache
from .l2_redis import L2RedisCache
from .l3_db import L3DbCache


class CacheManager:
    """Unified Cache Manager"""

    def __init__(self):
        self._l1 = L1LocalCache(
            max_size=getattr(settings, "L1_CACHE_MAX_SIZE", 1000),
            default_ttl=getattr(settings, "L1_CACHE_DEFAULT_TTL", 300)
        )
        self._l2 = L2RedisCache()
        self._l3 = L3DbCache()

    def _build_key(self, prefix: str, *args, **kwargs) -> str:
        """Build cache key from prefix and arguments"""
        key_parts = [prefix]

        for arg in args:
            key_parts.append(str(arg))

        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")

        key = ":".join(key_parts)

        if len(key) > 250:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}:{key_hash}"

        return key

    def get(self, key: str) -> Any | None:
        """Get value from cache layers"""
        value = self._l1.get(key)
        if value is not None:
            return value

        value = self._l2.get(key)
        if value is not None:
            self._l1.set(key, value)
            return value

        return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value to all cache layers"""
        self._l1.set(key, value, ttl)
        self._l2.set(key, value, ttl)

    def delete(self, key: str) -> None:
        """Delete value from all cache layers"""
        self._l1.delete(key)
        self._l2.delete(key)

    def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching pattern from all cache layers"""
        self._l1.clear_pattern(pattern)
        self._l2.clear_pattern(pattern)

    def cached(self, prefix: str, ttl: int | None = None):
        """Decorator for caching function results"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = self._build_key(prefix, *args, **kwargs)

                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                result = func(*args, **kwargs)

                if result is not None:
                    self.set(cache_key, result, ttl)

                return result

            return wrapper
        return decorator

    def invalidate(self, prefix: str, *args) -> None:
        """Invalidate all cached entries with given prefix and args"""
        key_prefix = self._build_key(prefix, *args)
        self.clear_pattern(f"{key_prefix}:")


cache_manager = CacheManager()


def clear_user_cache(user_id: int) -> None:
    """Clear all caches related to a specific user"""
    cache_manager.clear_pattern(f"user_detail:{user_id}:")
    cache_manager.clear_pattern(f"user_permissions:{user_id}:")
