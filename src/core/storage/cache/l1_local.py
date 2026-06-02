"""L1 Local Memory Cache

Implements in-memory local cache as a front layer to Redis (L1 Cache).
Supports LRU (Least Recently Used) and TTL (Time To Live) strategies.
"""

import time
from collections import OrderedDict
from typing import Any


class L1LocalCache:
    """L1 Local Memory Cache Implementation"""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize L1 cache.

        Args:
            max_size: Maximum number of items to store
            default_ttl: Default time to live in seconds
        """
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        """Get value by key"""
        if key not in self._cache:
            return None

        value, expire_time = self._cache[key]

        if time.time() >= expire_time:
            del self._cache[key]
            return None

        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Set value with optional TTL"""
        if key in self._cache:
            del self._cache[key]

        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)

        expire_time = time.time() + (ttl or self._default_ttl)
        self._cache[key] = (value, expire_time)

    def delete(self, key: str) -> None:
        """Delete value by key"""
        if key in self._cache:
            del self._cache[key]

    def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching pattern"""
        keys_to_delete = [k for k in self._cache if k.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]

    def clear(self) -> None:
        """Clear all cache entries"""
        self._cache.clear()

    def size(self) -> int:
        """Get current cache size"""
        return len(self._cache)
