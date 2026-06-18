"""缓存管理器

封装 L1（本地内存）和 L2（Redis）二级缓存的统一缓存管理器。
为所有缓存操作提供单一接口。

缓存键分层设计：
    - GLOBAL: global:{resource}:{key}
    - DATA: data:{tenant_id}:{resource}:{subject_type}:{subject_id}:{id}
    - LIST: list:{tenant_id}:{resource}:{action}:{scope}:{subject_type}:{subject_id}:{query_hash}

读取流程（读穿透）：
    L1本地缓存 -> L2 Redis缓存 -> 返回结果

写入流程（写穿透）：
    更新数据库 -> 删除L1缓存 -> 删除L2缓存
"""

import functools
import random
from typing import Any, Callable, Dict, Optional

from src.core.config import settings

from .cache_key import CacheType, build_cache_key
from .l1_local import L1LocalCache
from .l2_redis import L2RedisCache


class CacheManager:
    """统一缓存管理器

    封装 L1（本地内存）和 L2（Redis）二级缓存，提供统一的缓存操作接口。
    
    TTL 管理策略：
    - 默认 TTL 由配置文件统一控制（settings.L1_CACHE_TTL_MEDIUM / L2_CACHE_TTL_MEDIUM）
    - 调用时可指定具体 TTL（l1_ttl / l2_ttl），覆盖默认值
    - 支持使用配置常量：HIGH/MEDIUM/LOW（直接导入 settings 使用）
    """

    def __init__(self):
        """初始化缓存管理器

        创建并配置两层缓存：
        - L1: 本地内存缓存
        - L2: Redis分布式缓存
        """
        self._l1 = L1LocalCache(
            max_size=settings.L1_CACHE_MAXSIZE,
            default_ttl=settings.L1_CACHE_TTL_MEDIUM
        )
        self._l2 = L2RedisCache(
            default_ttl=settings.L2_CACHE_TTL_MEDIUM
        )

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

        offset_range = base_ttl * offset_percent / 100
        offset = random.uniform(-offset_range, offset_range)

        return max(1, int(base_ttl + offset))

    def _get_raw(self, key: str) -> Any | None:
        """原始获取缓存（不自动构建键）"""
        value = self._l1.get(key)
        if value is not None:
            return value

        value = self._l2.get(key)
        if value is not None:
            self._l1.set(key, value)
            return value

        return None

    def _set_raw(self, key: str, value: Any, l1_ttl: int | None = None, l2_ttl: int | None = None) -> None:
        """原始设置缓存（不自动构建键）"""
        final_l1_ttl = l1_ttl if l1_ttl is not None else settings.L1_CACHE_TTL_MEDIUM
        final_l2_ttl = l2_ttl if l2_ttl is not None else settings.L2_CACHE_TTL_MEDIUM

        l1_ttl_with_offset = self._calculate_ttl(final_l1_ttl, settings.L1_CACHE_RANDOM_OFFSET_PERCENT)
        l2_ttl_with_offset = self._calculate_ttl(final_l2_ttl, settings.L2_CACHE_RANDOM_OFFSET_PERCENT)

        self._l1.set(key, value, l1_ttl_with_offset)
        self._l2.set(key, value, l2_ttl_with_offset)

    def _delete_raw(self, key: str) -> None:
        """原始删除缓存（不自动构建键）"""
        self._l1.delete(key)
        self._l2.delete(key)

    def _clear_pattern_raw(self, pattern: str) -> None:
        """原始清除匹配模式的缓存（不自动构建键）"""
        self._l1.clear_pattern(pattern)
        self._l2.clear_pattern(pattern)

    def get(
        self,
        cache_type: str,
        resource: str,
        key: str = None,
        action: str = None,
        scope: str = None,
        query_params: Optional[Dict[str, Any]] = None,
        tenant_id: int = 0,
        subject_type: int = 0,
        subject_id: str = "anonymous",
    ) -> Any | None:
        """
        获取缓存

        Args:
            cache_type: 缓存类型（GLOBAL/DATA/LIST）
            resource: 资源名称（如goods、order）
            key: 业务层传入的key（单条数据的ID）
            action: 动作名称（列表查询时使用）
            scope: 数据范围
            query_params: 查询参数（列表查询时使用）
            tenant_id: 租户ID（DATA/LIST类型需要）
            subject_type: 主体类型（DATA/LIST类型需要）
            subject_id: 主体ID（DATA/LIST类型需要）

        Returns:
            缓存的值，如果未命中则返回None
        """
        full_key = build_cache_key(
            cache_type=cache_type,
            resource=resource,
            key=key,
            action=action,
            scope=scope,
            query_params=query_params,
            tenant_id=tenant_id,
            subject_type=subject_type,
            subject_id=subject_id,
        )
        return self._get_raw(full_key)

    def set(
        self,
        cache_type: str,
        resource: str,
        value: Any,
        key: str = None,
        action: str = None,
        scope: str = None,
        query_params: Optional[Dict[str, Any]] = None,
        l1_ttl: int | None = None,
        l2_ttl: int | None = None,
        tenant_id: int = 0,
        subject_type: int = 0,
        subject_id: str = "anonymous",
    ) -> None:
        """
        设置缓存

        Args:
            cache_type: 缓存类型（GLOBAL/DATA/LIST）
            resource: 资源名称
            value: 要缓存的值
            key: 业务层传入的key（单条数据的ID）
            action: 动作名称（列表查询时使用）
            scope: 数据范围
            query_params: 查询参数（列表查询时使用）
            l1_ttl: L1缓存过期时间（秒），不传则使用配置默认值
            l2_ttl: L2缓存过期时间（秒），不传则使用配置默认值
            tenant_id: 租户ID（DATA/LIST类型需要）
            subject_type: 主体类型（DATA/LIST类型需要）
            subject_id: 主体ID（DATA/LIST类型需要）
        
        TTL 配置建议（从 settings 导入）：
            - HIGH: 高频数据（用户会话、实时数据）
            - MEDIUM: 中频数据（字典数据、配置信息）
            - LOW: 低频数据（系统配置、权限数据）
        """
        full_key = build_cache_key(
            cache_type=cache_type,
            resource=resource,
            key=key,
            action=action,
            scope=scope,
            query_params=query_params,
            tenant_id=tenant_id,
            subject_type=subject_type,
            subject_id=subject_id,
        )
        self._set_raw(full_key, value, l1_ttl, l2_ttl)

    def delete(
        self,
        cache_type: str,
        resource: str,
        key: str = None,
        action: str = None,
        scope: str = None,
        tenant_id: int = 0,
        subject_type: int = 0,
        subject_id: str = "anonymous",
    ) -> None:
        """
        删除指定资源的缓存

        Args:
            cache_type: 缓存类型
            resource: 资源名称
            key: 不传则删除该资源下该用户的所有缓存
            action: 动作名称
            scope: 数据范围维度
            tenant_id: 租户ID（DATA/LIST类型需要）
            subject_type: 主体类型（DATA/LIST类型需要）
            subject_id: 主体ID（DATA/LIST类型需要）
        """
        if key:
            full_key = build_cache_key(
                cache_type=cache_type,
                resource=resource,
                key=key,
                action=action,
                scope=scope,
                tenant_id=tenant_id,
                subject_type=subject_type,
                subject_id=subject_id,
            )
            self._delete_raw(full_key)
        else:
            pattern = build_cache_key(
                cache_type=cache_type,
                resource=resource,
                key="*",
                action=action,
                scope=scope,
                tenant_id=tenant_id,
                subject_type=subject_type,
                subject_id=subject_id,
            )
            self._clear_pattern_raw(pattern)

    def delete_by_subject(
        self,
        subject_type: int,
        subject_id: int,
        tenant_id: int = 0
    ) -> None:
        """
        清除指定主体的所有缓存（权限变更时调用）

        Args:
            subject_type: 主体类型（0=用户，1=成员）
            subject_id: 主体ID
            tenant_id: 租户ID
        """
        pattern = f"*:{tenant_id}:*:{subject_type}:{subject_id}:*"
        self._clear_pattern_raw(pattern)

    def delete_by_tenant(self, tenant_id: int) -> None:
        """
        清除指定租户的所有缓存（租户删除时调用）

        Args:
            tenant_id: 租户ID
        """
        pattern = f"*:{tenant_id}:*"
        self._clear_pattern_raw(pattern)

    def get_global(self, resource: str, key: str) -> Any | None:
        """获取全局静态缓存"""
        return self.get(
            cache_type=CacheType.GLOBAL,
            resource=resource,
            key=key
        )

    def set_global(
        self,
        resource: str,
        key: str,
        value: Any,
        l1_ttl: int | None = None,
        l2_ttl: int | None = None
    ) -> None:
        """设置全局静态缓存

        Args:
            resource: 资源名称
            key: 缓存键
            value: 缓存值
            l1_ttl: L1缓存过期时间（秒），不传则使用 LOW 级别（最长）
            l2_ttl: L2缓存过期时间（秒），不传则使用 LOW 级别（最长）
        
        全局缓存默认使用最长 TTL（LOW级别），因为全局数据通常变化频率低。
        """
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

    def cached(
        self,
        resource: str,
        l1_ttl: int | None = None,
        l2_ttl: int | None = None,
        cache_type: str = None,
        tenant_id: int = 0,
        subject_type: int = 0,
        subject_id: str = "anonymous",
    ) -> Callable:
        """
        装饰器：自动缓存方法返回值

        Args:
            resource: 资源名称（如 user_detail）
            l1_ttl: L1缓存过期时间（秒），不传则使用配置默认值
            l2_ttl: L2缓存过期时间（秒），不传则使用配置默认值
            cache_type: 缓存类型（DATA/LIST/GLOBAL），不传则根据方法参数自动判断
            tenant_id: 租户ID（DATA/LIST类型需要）
            subject_type: 主体类型（DATA/LIST类型需要）
            subject_id: 主体ID（DATA/LIST类型需要）

        使用示例：
            @cache_manager.cached("user_detail", l1_ttl=300, l2_ttl=3600, tenant_id=1, subject_type=0, subject_id="456")
            def get_user_detail(self, user_id: int) -> dict:
                ...
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
                    tenant_id=tenant_id,
                    subject_type=subject_type,
                    subject_id=subject_id,
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
                        subject_type=subject_type,
                        subject_id=subject_id,
                    )
                
                return result
            
            return wrapper
        
        return decorator


cache_manager = CacheManager()


def clear_user_cache(user_id: int, tenant_id: int = 0) -> None:
    """清除指定用户的所有相关缓存

    Args:
        user_id: 用户 ID
        tenant_id: 租户ID
    """
    cache_manager.delete_by_subject(subject_type=0, subject_id=user_id, tenant_id=tenant_id)
