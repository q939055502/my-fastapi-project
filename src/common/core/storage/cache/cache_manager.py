"""缓存管理器

封装 L1（本地内存）、L2（Redis）和 L3（数据库）三级缓存的统一缓存管理器。
为所有缓存操作提供单一接口。

读取流程（读穿透）：
    L1本地缓存 -> L2 Redis缓存 -> L3数据库 -> 更新L2 -> 更新L1 -> 返回结果

写入流程（写穿透）：
    更新数据库 -> 删除L1缓存 -> 删除L2缓存
"""

import hashlib
import random
from collections.abc import Callable
from functools import wraps
from typing import Any

from src.common.core.config import settings

from .l1_local import L1LocalCache
from .l2_redis import L2RedisCache
from .l3_db import L3DbCache


class CacheManager:
    """统一缓存管理器

    封装 L1（本地内存）、L2（Redis）和 L3（数据库）三级缓存，提供统一的缓存操作接口。

    读取流程（读穿透）：
        L1本地缓存 -> L2 Redis缓存 -> L3数据库 -> 更新L2 -> 更新L1 -> 返回结果

    写入流程（写穿透）：
        更新数据库 -> 删除L1缓存 -> 删除L2缓存
    """

    def __init__(self):
        """初始化缓存管理器

        创建并配置三层缓存：
        - L1: 本地内存缓存
        - L2: Redis分布式缓存
        - L3: 数据库缓存（主要作为缓存源）
        """
        # 初始化 L1 本地缓存
        self._l1 = L1LocalCache(
            max_size=settings.L1_CACHE_MAXSIZE,
            default_ttl=settings.L1_CACHE_TTL_MEDIUM
        )
        # 初始化 L2 Redis 缓存
        self._l2 = L2RedisCache(
            default_ttl=settings.L2_CACHE_TTL_MEDIUM
        )
        # 初始化 L3 数据库缓存
        self._l3 = L3DbCache()

    def _calculate_ttl(self, base_ttl: int, offset_percent: int) -> int:
        """
        计算带随机偏移的 TTL，防止缓存雪崩。

        Args:
            base_ttl: 原始 TTL（秒）
            offset_percent: 随机偏移百分比（0-100）

        Returns:
            应用随机偏移后的 TTL
        """
        if not settings.CACHE_RANDOM_OFFSET_ENABLED or base_ttl <= 0:
            return base_ttl

        # 计算随机偏移范围
        offset_range = base_ttl * offset_percent / 100
        offset = random.uniform(-offset_range, offset_range)

        # 确保最小 TTL 为 1 秒
        return max(1, int(base_ttl + offset))

    def _build_key(self, prefix: str, *args, **kwargs) -> str:
        """根据前缀和参数构建缓存键

        Args:
            prefix: 缓存键前缀
            *args: 位置参数，将被转换为字符串并拼接
            **kwargs: 关键字参数，按键名排序后拼接

        Returns:
            构建完成的缓存键字符串

        Note:
            如果最终键长度超过 250 字符，会使用 MD5 哈希生成短键，以避免键过长
        """
        key_parts = [prefix]

        # 拼接位置参数
        for arg in args:
            key_parts.append(str(arg))

        # 按键名排序后拼接关键字参数
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")

        # 使用冒号连接所有部分
        key = ":".join(key_parts)

        # 如果键太长，使用 MD5 哈希缩短
        if len(key) > 250:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{prefix}:{key_hash}"

        return key

    def get(self, key: str) -> Any | None:
        """从缓存层获取值

        读取流程：
        1. 先从 L1 本地缓存获取，命中则直接返回
        2. L1 未命中则从 L2 Redis 缓存获取，命中则同时更新 L1 缓存
        3. L2 也未命中则返回 None（不再查询 L3 数据库，需由业务层处理）

        Args:
            key: 缓存键

        Returns:
            缓存的值，如果都未命中则返回 None
        """
        # 先从 L1 本地缓存获取
        value = self._l1.get(key)
        if value is not None:
            return value

        # L1 未命中，从 L2 Redis 缓存获取
        value = self._l2.get(key)
        if value is not None:
            # L2 命中，同步更新 L1 缓存（使用默认 L1 TTL）
            self._l1.set(key, value)
            return value

        # 都未命中
        return None

    def set(self, key: str, value: Any, l1_ttl: int | None = None, l2_ttl: int | None = None) -> None:
        """设置值到所有缓存层

        同时写入 L1 和 L2 缓存，确保数据一致性

        Args:
            key: 缓存键
            value: 要缓存的值
            l1_ttl: L1 缓存过期时间（秒），如果为 None 则使用配置中的 L1_CACHE_TTL_MEDIUM
            l2_ttl: L2 缓存过期时间（秒），如果为 None 则使用配置中的 L2_CACHE_TTL_MEDIUM
        """
        # 确定各层的 TTL
        final_l1_ttl = l1_ttl if l1_ttl is not None else settings.L1_CACHE_TTL_MEDIUM
        final_l2_ttl = l2_ttl if l2_ttl is not None else settings.L2_CACHE_TTL_MEDIUM

        # 计算带随机偏移的 TTL
        l1_ttl_with_offset = self._calculate_ttl(final_l1_ttl, settings.L1_CACHE_RANDOM_OFFSET_PERCENT)
        l2_ttl_with_offset = self._calculate_ttl(final_l2_ttl, settings.L2_CACHE_RANDOM_OFFSET_PERCENT)

        self._l1.set(key, value, l1_ttl_with_offset)
        self._l2.set(key, value, l2_ttl_with_offset)

    def delete(self, key: str) -> None:
        """从所有缓存层删除值

        同时删除 L1 和 L2 缓存中的指定键

        Args:
            key: 要删除的缓存键
        """
        self._l1.delete(key)
        self._l2.delete(key)

    def clear_pattern(self, pattern: str) -> None:
        """从所有缓存层清除匹配模式的键

        清除所有匹配指定模式的缓存键

        Args:
            pattern: 缓存键模式，支持通配符
        """
        self._l1.clear_pattern(pattern)
        self._l2.clear_pattern(pattern)

    def cached(self, prefix: str, l1_ttl: int | None = None, l2_ttl: int | None = None):
        """缓存函数结果的装饰器

        自动缓存函数返回值，下次调用时优先从缓存获取

        Args:
            prefix: 缓存键前缀
            l1_ttl: L1 缓存过期时间（秒），如果为 None 则使用配置中的 L1_CACHE_TTL_MEDIUM
            l2_ttl: L2 缓存过期时间（秒），如果为 None 则使用配置中的 L2_CACHE_TTL_MEDIUM

        Returns:
            装饰后的函数
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 根据函数参数构建缓存键
                cache_key = self._build_key(prefix, *args, **kwargs)

                # 尝试从缓存获取
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # 缓存未命中，执行原函数
                result = func(*args, **kwargs)

                # 将结果存入缓存（仅缓存非 None 结果）
                if result is not None:
                    self.set(cache_key, result, l1_ttl, l2_ttl)

                return result

            return wrapper
        return decorator

    def invalidate(self, prefix: str, *args) -> None:
        """使指定前缀的所有缓存失效

        清除所有匹配指定前缀和参数的缓存条目

        Args:
            prefix: 缓存键前缀
            *args: 用于构建键前缀的位置参数
        """
        key_prefix = self._build_key(prefix, *args)
        self.clear_pattern(f"{key_prefix}:")


# 全局缓存管理器实例
cache_manager = CacheManager()


def clear_user_cache(user_id: int) -> None:
    """清除指定用户的所有相关缓存

    Args:
        user_id: 用户 ID
    """
    cache_manager.clear_pattern(f"user_detail:{user_id}:")
    cache_manager.clear_pattern(f"user_permissions:{user_id}:")
