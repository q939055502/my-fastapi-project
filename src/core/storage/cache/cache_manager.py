"""统一缓存管理器（Tag 版本哈希型）

封装 L1(本地内存) + L2(Redis) 二级缓存。
通过 TagStore 管理标签版本，标签版本变化 → tag_hash 变化 → 旧缓存键自然失效。

缓存键格式:
    - GLOBAL: global:{tag_hash}:{resource}:{key}
    - DATA:   data:{tag_hash}:{tenant_id}:{resource}:{key}
    - LIST:   list:{tag_hash}:{tenant_id}:{resource}:{query_hash}

核心概念:
    - tags: 缓存依赖的标签列表，任一标签版本变化则缓存失效
    - tag_hash: 由所有标签+版本号计算出的哈希，嵌入缓存键
    - invalidate(tags): 递增标签版本，使关联缓存逻辑失效

底层使用 dogpile.cache 框架实现，支持分布式锁防止缓存击穿。

注意:
    - tenant_id 保留用于租户隔离(不同租户数据物理隔离)
    - 数据范围过滤由业务层(Service)负责，不在缓存层处理
    - 缓存值必须是可 JSON 序列化的纯数据结构，禁止缓存 ORM 对象
"""

import functools
from collections.abc import Callable
from typing import Any

from src.core.config import settings

from .cache_key import CacheType, build_cache_key
from . import dogpile_config as _dc
from .tag_store import tag_store


class CacheManager:
    """统一缓存管理器

    封装 dogpile.cache 的两级缓存，提供统一的缓存操作接口。
    通过标签版本哈希实现缓存失效: 递增标签版本 → tag_hash 变化 → 旧键自然过期。

    TTL 管理策略:
    - 默认 TTL 由配置文件统一控制(settings.L1_CACHE_TTL_MEDIUM / L2_CACHE_TTL_MEDIUM)
    - 调用时可指定具体 TTL(l1_ttl / l2_ttl),覆盖默认值
    - 支持使用配置常量:HIGH/MEDIUM/LOW(直接导入 settings 使用)
    """

    # ====================
    # 新接口（推荐使用）
    # ====================

    def get(
        self,
        cache_type: str,
        resource: str,
        key: str | None = None,
        tags: list[str] | None = None,
        query_params: dict[str, Any] | None = None,
        tenant_id: int = 0,
    ) -> Any | None:
        """读取缓存

        Args:
            cache_type: 缓存类型 (CacheType.GLOBAL / DATA / LIST)
            resource: 资源名称
            key: 数据主键 (GLOBAL/DATA 类型使用)
            tags: 依赖标签列表，用于精准失效
            query_params: 查询参数 (LIST 类型使用)
            tenant_id: 租户ID (DATA/LIST 类型使用)
        """
        tag_hash = tag_store.calc_tag_hash(tags)
        full_key = build_cache_key(
            cache_type=cache_type,
            resource=resource,
            key=key,
            query_params=query_params,
            tenant_id=tenant_id,
            tag_hash=tag_hash,
        )
        return self._get_raw(full_key)

    def set(
        self,
        cache_type: str,
        resource: str,
        value: Any,
        key: str | None = None,
        tags: list[str] | None = None,
        query_params: dict[str, Any] | None = None,
        tenant_id: int = 0,
        l1_ttl: int | None = None,
        l2_ttl: int | None = None,
    ) -> None:
        """写入缓存

        Args:
            cache_type: 缓存类型 (CacheType.GLOBAL / DATA / LIST)
            resource: 资源名称
            value: 缓存值(必须是可 JSON 序列化的纯数据结构)
            key: 数据主键 (GLOBAL/DATA 类型使用)
            tags: 依赖标签列表，用于精准失效
            query_params: 查询参数 (LIST 类型使用)
            tenant_id: 租户ID (DATA/LIST 类型使用)
            l1_ttl: L1 本地缓存 TTL(秒),None 用默认值
            l2_ttl: L2 Redis 缓存 TTL(秒),None 用默认值
        """
        tag_hash = tag_store.calc_tag_hash(tags)
        full_key = build_cache_key(
            cache_type=cache_type,
            resource=resource,
            key=key,
            query_params=query_params,
            tenant_id=tenant_id,
            tag_hash=tag_hash,
        )
        self._set_raw(full_key, value, l1_ttl, l2_ttl)

    def invalidate(self, tags: list[str]) -> None:
        """失效缓存（递增标签版本，旧缓存键自然过期）

        Args:
            tags: 要失效的标签列表，如 ["role:1", "role:all"]
        """
        tag_store.invalidate(tags)

    def cached(
        self,
        resource: str,
        tags: list[str] | None = None,
        l1_ttl: int | None = None,
        l2_ttl: int | None = None,
        cache_type: str = None,
        tenant_id: int = 0,
    ) -> Callable:
        """装饰器：自动缓存方法返回值

        Args:
            resource: 资源名称
            tags: 依赖标签列表
            l1_ttl: L1 TTL(秒)
            l2_ttl: L2 TTL(秒)
            cache_type: 缓存类型,默认 DATA
            tenant_id: 租户ID
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                key_parts = [func.__name__]
                for i, arg in enumerate(args[1:], 1):
                    if arg is not None:
                        key_parts.append(f"arg{i}_{arg}")
                for k, v in sorted(kwargs.items()):
                    if v is not None:
                        key_parts.append(f"{k}_{v}")
                key = "_".join(key_parts)

                final_cache_type = cache_type or CacheType.DATA
                cached_result = self.get(
                    cache_type=final_cache_type,
                    resource=resource,
                    key=key,
                    tags=tags,
                    tenant_id=tenant_id,
                )
                if cached_result is not None:
                    return cached_result

                result = func(*args, **kwargs)

                if result is not None:
                    self.set(
                        cache_type=final_cache_type,
                        resource=resource,
                        key=key,
                        value=result,
                        tags=tags,
                        l1_ttl=l1_ttl,
                        l2_ttl=l2_ttl,
                        tenant_id=tenant_id,
                    )
                return result

            return wrapper
        return decorator

    # ====================
    # 底层读写（内部使用）
    # ====================

    def _calculate_l1_ttl(self, base_ttl: int) -> int:
        return _dc._calculate_ttl(base_ttl, settings.L1_CACHE_RANDOM_OFFSET_PERCENT)

    def _calculate_l2_ttl(self, base_ttl: int) -> int:
        return _dc._calculate_ttl(base_ttl, settings.L2_CACHE_RANDOM_OFFSET_PERCENT)

    def _get_raw(self, key: str) -> Any | None:
        value = _dc.l1_get(key)
        if value is not None:
            return value
        value = _dc.l2_get(key)
        if value is not None:
            _dc.l1_set(key, value)
            return value
        return None

    def _set_raw(self, key: str, value: Any, l1_ttl: int | None = None, l2_ttl: int | None = None) -> None:
        final_l1_ttl = l1_ttl if l1_ttl is not None else settings.L1_CACHE_TTL_MEDIUM
        final_l2_ttl = l2_ttl if l2_ttl is not None else settings.L2_CACHE_TTL_MEDIUM
        _dc.l1_set(key, value, ttl=self._calculate_l1_ttl(final_l1_ttl))
        _dc.l2_set(key, value, ttl=self._calculate_l2_ttl(final_l2_ttl))

    def _delete_raw(self, key: str) -> None:
        _dc.l1_delete(key)
        _dc.l2_delete(key)

    def _clear_pattern_raw(self, pattern: str) -> None:
        """[废弃] 按模式物理删除，仅保留供旧接口过渡使用"""
        _dc.l1_clear_pattern(pattern)
        _dc.l2_clear_pattern(pattern)

    # ====================
    # 旧接口（废弃，过渡期保留）
    # ====================
    # 旧接口内部调用新接口，用表级标签 "{resource}:all" 作为默认 tag。
    # 功能不 break，行为从"版本号递增"变为"表级标签递增"，效果等价。
    # 业务层后续逐步迁移到新接口，传入更精细的 tags。
    # 迁移完成后移除以下所有方法。

    def get_global(self, resource: str, key: str) -> Any | None:
        """[废弃] 使用 get(cache_type=GLOBAL, ...) 替代"""
        return self.get(
            cache_type=CacheType.GLOBAL,
            resource=resource,
            key=key,
            tags=[f"{resource}:all"],
        )

    def set_global(
        self, resource: str, key: str, value: Any,
        l1_ttl: int | None = None, l2_ttl: int | None = None,
    ) -> None:
        """[废弃] 使用 set(cache_type=GLOBAL, ...) 替代"""
        final_l1_ttl = l1_ttl if l1_ttl is not None else settings.L1_CACHE_TTL_LOW
        final_l2_ttl = l2_ttl if l2_ttl is not None else settings.L2_CACHE_TTL_LOW
        self.set(
            cache_type=CacheType.GLOBAL,
            resource=resource,
            key=key,
            value=value,
            tags=[f"{resource}:all"],
            l1_ttl=final_l1_ttl,
            l2_ttl=final_l2_ttl,
        )

    def delete_global(self, resource: str, key: str) -> None:
        """[废弃] 使用 invalidate(tags=[...]) 替代"""
        self.invalidate([f"{resource}:all"])

    def delete(
        self,
        cache_type: str,
        resource: str,
        key: str = None,
        tenant_id: int = 0,
        namespace: str = "default",
    ) -> None:
        """[废弃] 使用 invalidate(tags=[...]) 替代"""
        self.invalidate([f"{resource}:all"])

    def delete_by_tenant(self, tenant_id: int) -> None:
        """[废弃] 使用 invalidate(tags=[f"tenant:{tenant_id}"]) 替代"""
        self.invalidate([f"tenant:{tenant_id}"])

    def increment_version(self, namespace: str = "default") -> int:
        """[废弃] 使用 invalidate(tags=[...]) 替代"""
        self.invalidate([f"{namespace}:all"])
        return 0

    def get_version(self, namespace: str = "default") -> int:
        """[废弃] 版本号机制已被 tag 机制替代"""
        return tag_store.get_tag_version(f"{namespace}:all")

    def set_version(self, version: int, namespace: str = "default") -> int:
        """[废弃] 版本号机制已被 tag 机制替代"""
        return version

    def reset_version(self, namespace: str = "default") -> int:
        """[废弃] 版本号机制已被 tag 机制替代"""
        return 0


cache_manager = CacheManager()


def clear_user_cache(user_id: int, tenant_id: int = 0) -> None:
    """[废弃] 清除指定用户的所有相关缓存

    使用 invalidate(tags=["user:{user_id}", "user:all"]) 替代。
    """
    cache_manager.invalidate([f"user:{user_id}", "user:all"])
