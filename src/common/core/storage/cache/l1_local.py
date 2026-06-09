"""L1 本地内存缓存

实现基于内存的本地缓存，作为 Redis 的前端缓存层（L1 Cache）。
支持 LRU（最近最少使用）和 TTL（生存时间）策略。
"""


import time
from collections import OrderedDict
from typing import Any


class L1LocalCache:
    """L1 本地内存缓存实现"""

    def __init__(
        self,
        max_size: int = 1000,
        default_ttl: int = 300
    ):
        """
        初始化 L1 缓存。

        Args:
            max_size: 最大存储条目数
            default_ttl: 默认生存时间（秒）
        """
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        """根据键获取值"""
        if key not in self._cache:
            return None

        value, expire_time = self._cache[key]

        # 检查是否过期
        if time.time() >= expire_time:
            del self._cache[key]
            return None

        # 将访问的键移到末尾（LRU 策略）
        self._cache.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """设置值，可选指定 TTL

        注意：这里不处理随机偏移，由缓存管理器统一处理

        Args:
            key: 缓存键
            value: 要缓存的值
            ttl: 过期时间（秒），如果为 None 则使用默认 TTL
        """
        # 如果键已存在，先删除
        if key in self._cache:
            del self._cache[key]

        # 如果缓存已满，删除最久未使用的条目（LRU 策略）
        if len(self._cache) >= self._max_size:
            self._cache.popitem(last=False)

        # 计算过期时间
        final_ttl = ttl if ttl is not None else self._default_ttl
        expire_time = time.time() + final_ttl
        self._cache[key] = (value, expire_time)

    def delete(self, key: str) -> None:
        """根据键删除值"""
        if key in self._cache:
            del self._cache[key]

    def clear_pattern(self, pattern: str) -> None:
        """清除所有匹配模式的键"""
        keys_to_delete = [k for k in self._cache if k.startswith(pattern)]
        for key in keys_to_delete:
            del self._cache[key]

    def clear(self) -> None:
        """清除所有缓存条目"""
        self._cache.clear()

    def size(self) -> int:
        """获取当前缓存大小"""
        return len(self._cache)
