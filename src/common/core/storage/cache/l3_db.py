"""L3 Database Proxy

Implements database proxy as the third layer (L3 Cache).
Serves as a fallback when L1 and L2 caches miss.
"""

from collections.abc import Callable
from typing import Any


class L3DbCache:
    """L3 Database Proxy Implementation"""

    def __init__(self):
        """Initialize database proxy"""
        pass

    def get(self, key: str, fetch_func: Callable[[], Any]) -> Any:
        """
        Fetch data from database using provided function.

        Args:
            key: Cache key (not used directly, kept for interface consistency)
            fetch_func: Function to fetch data from database

        Returns:
            Data fetched from database
        """
        return fetch_func()

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        This is a no-op for L3 as database writes happen separately.
        The actual database update should happen before cache invalidation.
        """
        pass

    def delete(self, key: str) -> None:
        """
        This is a no-op for L3 as database deletes happen separately.
        """
        pass

    def clear_pattern(self, pattern: str) -> None:
        """
        This is a no-op for L3 as database clearing happens separately.
        """
        pass
