"""dogpile.cache 两级缓存配置

配置两级缓存区域：
- L1: dogpile.cache.memory（本地内存，高速，容量小，进程内共享）
- L2: dogpile.cache.redis（分布式共享，中速，容量大，跨进程共享）

提供二级缓存的底层读写接口，供 CacheManager 调用。

注意：
- Redis 不可用时 L2 自动降级为无，L1 正常工作
- 序列化使用 JSON，缓存值必须是可 JSON 序列化的纯数据结构
"""

import json
import random
from typing import Any

from dogpile.cache import make_region
from dogpile.cache.api import NO_VALUE

from src.core.config import settings


def _json_loads(value: bytes) -> Any:
    return json.loads(value.decode("utf-8"))


def _json_dumps(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


# L1 本地内存缓存
l1_region = make_region(
    name="l1_memory",
    function_key_generator=lambda fn, namespace, args, kwargs: None,
).configure(
    "dogpile.cache.memory",
    expiration_time=settings.L1_CACHE_TTL_MEDIUM,
    arguments={
        "max_entries": settings.L1_CACHE_MAXSIZE,
    },
)

# L2 Redis 分布式缓存
_l2_available = False
l2_region = make_region(name="l2_redis")

try:
    l2_region.configure(
        "dogpile.cache.redis",
        expiration_time=settings.L2_CACHE_TTL_MEDIUM,
        arguments={
            "url": settings.REDIS_URL,
            "redis_expiration_time": settings.L2_CACHE_TTL_MEDIUM,
            "distributed_lock": True,
            "thread_local_lock": False,
            "lock_timeout": 10,
        },
    )
    _l2_available = True
except Exception:
    _l2_available = False


def is_l2_available() -> bool:
    """检查 L2 Redis 缓存是否可用"""
    return _l2_available


def _calculate_ttl(base_ttl: int, offset_percent: int) -> int:
    """计算带随机偏移的 TTL，防止缓存雪崩"""
    if not settings.CACHE_RANDOM_OFFSET_ENABLED or base_ttl <= 0:
        return base_ttl
    offset_range = base_ttl * offset_percent / 100
    offset = random.uniform(-offset_range, offset_range)
    return max(1, int(base_ttl + offset))


def l1_get(key: str) -> Any | None:
    """从 L1 缓存获取值"""
    value = l1_region.get(key)
    if value is NO_VALUE:
        return None
    return value


def l1_set(key: str, value: Any, ttl: int | None = None) -> None:
    """写入 L1 缓存"""
    if ttl is not None:
        l1_region.set(key, value, expiration_time=ttl)
    else:
        l1_region.set(key, value)


def l1_delete(key: str) -> None:
    """删除 L1 缓存"""
    l1_region.delete(key)


def l2_get(key: str) -> Any | None:
    """从 L2 缓存获取值"""
    if not _l2_available:
        return None
    try:
        value = l2_region.get(key)
        if value is NO_VALUE:
            return None
        return value
    except Exception:
        return None


def l2_set(key: str, value: Any, ttl: int | None = None) -> None:
    """写入 L2 缓存"""
    if not _l2_available:
        return
    try:
        if ttl is not None:
            l2_region.set(key, value, expiration_time=ttl)
        else:
            l2_region.set(key, value)
    except Exception:
        pass


def l2_delete(key: str) -> None:
    """删除 L2 缓存"""
    if not _l2_available:
        return
    try:
        l2_region.delete(key)
    except Exception:
        pass


def l2_get_int(key: str) -> int:
    """从 Redis 读取整数值"""
    if not _l2_available:
        return 0
    try:
        raw = l2_region.backend.writer_client.get(key)
        if raw is not None:
            return int(raw)
    except Exception:
        pass
    return 0


def l2_incr(key: str) -> int:
    """Redis 原子递增，返回递增后的值"""
    if not _l2_available:
        return 0
    try:
        return l2_region.backend.writer_client.incr(key)
    except Exception:
        return 0


def l2_get_version(version_key: str) -> int:
    """[废弃] 从 Redis 获取版本号，使用 l2_get_int 替代"""
    return l2_get_int(version_key)


def l2_set_version(version_key: str, version: int) -> None:
    """[废弃] 设置 Redis 版本号，使用 l2_incr 替代"""
    if not _l2_available:
        return
    try:
        l2_region.backend.writer_client.set(version_key, version)
    except Exception:
        pass


def l2_clear_pattern(pattern: str) -> None:
    """按模式清除 L2 缓存"""
    if not _l2_available:
        return
    try:
        client = l2_region.backend.writer_client
        keys = client.keys(f"{pattern}*")
        if keys:
            client.delete(*keys)
    except Exception:
        pass


def l1_clear_pattern(pattern: str) -> None:
    """按前缀清除 L1 缓存"""
    cache_dict = getattr(l1_region.backend, "_cache", {})
    keys_to_delete = [k for k in cache_dict if k.startswith(pattern)]
    for key in keys_to_delete:
        l1_region.delete(key)
