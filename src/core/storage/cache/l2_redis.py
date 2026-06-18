"""L2 Redis 分布式缓存

实现基于 Redis 的分布式缓存作为第二层缓存（L2 Cache）。
提供跨进程/服务的持久化共享缓存能力。
"""

import json
from typing import Any

import redis
from redis import Redis
from src.core.config import settings


class L2RedisCache:
    """L2 Redis 分布式缓存实现"""

    def __init__(self, default_ttl: int | None = None):
        """
        初始化 Redis 连接

        Args:
            default_ttl: 默认缓存过期时间（秒），不指定则使用配置中的 L2_CACHE_TTL_MEDIUM
        """
        self._client = None
        self._default_ttl = default_ttl or settings.L2_CACHE_TTL_MEDIUM
        self._connect()

    def _connect(self):
        """建立 Redis 连接"""
        try:
            self._client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5,
            )
            self._client.ping()
        except Exception:
            self._client = None

    def _ensure_connection(self) -> Redis | None:
        """确保 Redis 连接已建立"""
        if self._client is None:
            self._connect()
        return self._client

    def get(self, key: str) -> Any | None:
        """根据键获取值"""
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
        """设置值，可选指定 TTL

        注意：这里不处理随机偏移，由缓存管理器统一处理

        Args:
            key: 缓存键
            value: 要缓存的值
            ttl: 过期时间（秒），如果为 None 则使用默认 TTL
        """
        client = self._ensure_connection()
        if not client:
            return

        try:
            value_str = json.dumps(value)
            final_ttl = ttl if ttl is not None else self._default_ttl
            if final_ttl:
                client.setex(key, final_ttl, value_str)
            else:
                client.set(key, value_str)
        except Exception:
            pass

    def delete(self, key: str) -> None:
        """根据键删除值"""
        client = self._ensure_connection()
        if not client:
            return

        try:
            client.delete(key)
        except Exception:
            pass

    def clear_pattern(self, pattern: str) -> None:
        """清除所有匹配模式的键"""
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
        """清除所有缓存条目"""
        client = self._ensure_connection()
        if not client:
            return

        try:
            client.flushdb()
        except Exception:
            pass
