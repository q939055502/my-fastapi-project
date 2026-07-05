"""统一缓存管理器

封装 L1(本地内存) 和 L2(Redis)二级缓存的统一缓存管理器。
底层使用 dogpile.cache 框架实现，支持分布式锁防止缓存击穿。
提供版本号机制，修改版本号即可让某 namespace 下所有缓存失效。

缓存键分层设计(版本号嵌入，失效即全换):
    - GLOBAL: global:{version}:{resource}:{key}
    - DATA:   data:{version}:{tenant_id}:{resource}:{key}
    - LIST:   list:{version}:{tenant_id}:{resource}:{query_hash}

版本号存储:
    - Redis: cache:version:{namespace}  (分布式共享)
    - L1:    self._versions[namespace]  (本地缓存，Redis 不可用时兜底)
    默认 namespace = "default",缓存通用。

读取流程(读穿透):
    L1本地缓存 -> L2 Redis缓存 -> 返回结果

写入流程(写穿透):
    更新数据后 -> 删除L1缓存 -> 删除L2缓存

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

DEFAULT_NAMESPACE = "default"
VERSION_KEY_PREFIX = "cache:version:"


class CacheManager:
    """统一缓存管理器

    封装 dogpile.cache 的两级缓存，提供统一的缓存操作接口。
    支持 namespace 版本号递增，让某一范围缓存整体失效。

    TTL 管理策略:
    - 默认 TTL 由配置文件统一控制(settings.L1_CACHE_TTL_MEDIUM / L2_CACHE_TTL_MEDIUM)
    - 调用时可指定具体 TTL(l1_ttl / l2_ttl),覆盖默认值
    - 支持使用配置常量:HIGH/MEDIUM/LOW(直接导入 settings 使用)
    """

    def __init__(self):
        self._versions: dict[str, int] = {}

    # ---------- 版本号管理 ----------

    def _get_version(self, namespace: str) -> int:
        if _dc.is_l2_available():
            key = f"{VERSION_KEY_PREFIX}{namespace}"
            version = _dc.l2_get_version(key)
            if version > 0:
                self._versions[namespace] = version
                return version
        return self._versions.get(namespace, 0)

    def _set_version(self, namespace: str, version: int) -> None:
        self._versions[namespace] = version
        if _dc.is_l2_available():
            key = f"{VERSION_KEY_PREFIX}{namespace}"
            _dc.l2_set_version(key, version)

    def get_version(self, namespace: str = DEFAULT_NAMESPACE) -> int:
        """查询当前缓存版本号"""
        return self._get_version(namespace)

    def set_version(self, version: int, namespace: str = DEFAULT_NAMESPACE) -> int:
        """手动设置版本号，返回设置后的版本号"""
        self._set_version(namespace, version)
        return version

    def increment_version(self, namespace: str = DEFAULT_NAMESPACE) -> int:
        """版本号自增，返回自增后的版本号

        该 namespace 下所有缓存键都会变成 v{new}，旧键自然过期。
        """
        new_version = self._get_version(namespace) + 1
        self._set_version(namespace, new_version)
        return new_version

    def reset_version(self, namespace: str = DEFAULT_NAMESPACE) -> int:
        """重置版本号为 0

        慎用：Redis 中旧版本号数据若未清，重启后会短暂命中旧键(直到TTL过期)。
        """
        self._set_version(namespace, 0)
        return 0

    # ---------- 缓存核心 ----------

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
        l1_ttl_with_offset = self._calculate_l1_ttl(final_l1_ttl)
        l2_ttl_with_offset = self._calculate_l2_ttl(final_l2_ttl)
        _dc.l1_set(key, value, ttl=l1_ttl_with_offset)
        _dc.l2_set(key, value, ttl=l2_ttl_with_offset)

    def _delete_raw(self, key: str) -> None:
        _dc.l1_delete(key)
        _dc.l2_delete(key)

    def _clear_pattern_raw(self, pattern: str) -> None:
        _dc.l1_clear_pattern(pattern)
        _dc.l2_clear_pattern(pattern)

    # ---------- 对外接口 ----------

    def get(
        self,
        cache_type: str,
        resource: str,
        key: str = None,
        query_params: dict[str, Any] | None = None,
        tenant_id: int = 0,
        namespace: str = DEFAULT_NAMESPACE,
    ) -> Any | None:
        full_key = build_cache_key(
            cache_type=cache_type,
            resource=resource,
            key=key,
            query_params=query_params,
            tenant_id=tenant_id,
            version=self._get_version(namespace),
        )
        return self._get_raw(full_key)

    def set(
        self,
        cache_type: str,
        resource: str,
        value: Any,
        key: str = None,
        query_params: dict[str, Any] | None = None,
        l1_ttl: int | None = None,
        l2_ttl: int | None = None,
        tenant_id: int = 0,
        namespace: str = DEFAULT_NAMESPACE,
    ) -> None:
        full_key = build_cache_key(
            cache_type=cache_type,
            resource=resource,
            key=key,
            query_params=query_params,
            tenant_id=tenant_id,
            version=self._get_version(namespace),
        )
        self._set_raw(full_key, value, l1_ttl, l2_ttl)

    def delete(
        self,
        cache_type: str,
        resource: str,
        key: str = None,
        tenant_id: int = 0,
        namespace: str = DEFAULT_NAMESPACE,
    ) -> None:
        version = self._get_version(namespace)
        if key:
            full_key = build_cache_key(
                cache_type=cache_type,
                resource=resource,
                key=key,
                tenant_id=tenant_id,
                version=version,
            )
            self._delete_raw(full_key)
        else:
            pattern = build_cache_key(
                cache_type=cache_type,
                resource=resource,
                key="*",
                tenant_id=tenant_id,
                version=version,
            )
            self._clear_pattern_raw(pattern)

    def delete_by_tenant(self, tenant_id: int) -> None:
        pattern = f"*:{tenant_id}:*"
        self._clear_pattern_raw(pattern)

    def get_global(self, resource: str, key: str) -> Any | None:
        return self.get(cache_type=CacheType.GLOBAL, resource=resource, key=key)

    def set_global(
        self,
        resource: str,
        key: str,
        value: Any,
        l1_ttl: int | None = None,
        l2_ttl: int | None = None
    ) -> None:
        final_l1_ttl = l1_ttl if l1_ttl is not None else settings.L1_CACHE_TTL_LOW
        final_l2_ttl = l2_ttl if l2_ttl is not None else settings.L2_CACHE_TTL_LOW
        self.set(
            cache_type=CacheType.GLOBAL,
            resource=resource,
            key=key,
            value=value,
            l1_ttl=final_l1_ttl,
            l2_ttl=final_l2_ttl
        )

    def delete_global(self, resource: str, key: str) -> None:
        self.delete(cache_type=CacheType.GLOBAL, resource=resource, key=key)

    def cached(
        self,
        resource: str,
        l1_ttl: int | None = None,
        l2_ttl: int | None = None,
        cache_type: str = None,
        tenant_id: int = 0,
        namespace: str = DEFAULT_NAMESPACE,
    ) -> Callable:
        """装饰器：自动缓存方法返回值"""
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
                    tenant_id=tenant_id,
                    namespace=namespace,
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
                        l1_ttl=l1_ttl,
                        l2_ttl=l2_ttl,
                        tenant_id=tenant_id,
                        namespace=namespace,
                    )
                return result

            return wrapper
        return decorator


cache_manager = CacheManager()


def clear_user_cache(user_id: int, tenant_id: int = 0) -> None:
    """清除指定用户的所有相关缓存

    注意：由于缓存层不再存储subject维度信息，此方法改为递增版本号
    让该租户下所有缓存失效。如需更精细的失效控制，请在业务层实现。
    """
    cache_manager.increment_version(namespace=f"user_{user_id}")
