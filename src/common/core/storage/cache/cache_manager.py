"""缓存管理器

封装 L1（本地内存）、L2（Redis）和 L3（数据库）三级缓存的统一缓存管理器。
为所有缓存操作提供单一接口，自动注入权限维度。

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
import hashlib
import random
from typing import Any, Callable, Dict, Optional

from src.common.core.config import settings

from .l1_local import L1LocalCache
from .l2_redis import L2RedisCache
from .l3_db import L3DbCache


class CacheManager:
    """统一缓存管理器

    封装 L1（本地内存）、L2（Redis）和 L3（数据库）三级缓存，提供统一的缓存操作接口。
    自动注入权限维度，支持分层缓存键设计。
    
    TTL 管理策略：
    - 默认 TTL 由配置文件统一控制（settings.L1_CACHE_TTL_MEDIUM / L2_CACHE_TTL_MEDIUM）
    - 调用时可指定具体 TTL（l1_ttl / l2_ttl），覆盖默认值
    - 支持使用配置常量：HIGH/MEDIUM/LOW（直接导入 settings 使用）
    """

    class CacheType:
        """缓存类型枚举"""
        GLOBAL = "global"
        DATA = "data"
        LIST = "list"

    def __init__(self):
        """初始化缓存管理器

        创建并配置三层缓存：
        - L1: 本地内存缓存
        - L2: Redis分布式缓存
        - L3: 数据库缓存（主要作为缓存源）
        """
        # 初始化 L1 本地缓存（使用中级别 TTL）
        self._l1 = L1LocalCache(
            max_size=settings.L1_CACHE_MAXSIZE,
            default_ttl=settings.L1_CACHE_TTL_MEDIUM
        )
        # 初始化 L2 Redis 缓存（使用中级别 TTL）
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

        offset_range = base_ttl * offset_percent / 100
        offset = random.uniform(-offset_range, offset_range)

        return max(1, int(base_ttl + offset))

    def _build_cache_key(
        self,
        cache_type: str,
        resource: str,
        key: Optional[str] = None,
        action: Optional[str] = None,
        scope: Optional[str] = None,
        query_params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        自动构建包含权限维度的缓存键（核心方法）

        Args:
            cache_type: 缓存类型（GLOBAL/DATA/LIST）
            resource: 资源名称
            key: 业务键（单条数据的ID）
            action: 动作名称（列表查询时使用）
            scope: 数据范围
            query_params: 查询参数（列表查询时使用）

        Returns:
            完整的缓存键字符串
        """
        from src.common.core.context import get_current_tenant_id, get_current_subject_type, get_current_subject_id

        parts = [cache_type]

        if cache_type == self.CacheType.GLOBAL:
            parts.append(resource)
            if key:
                parts.append(key)
            return ":".join(parts)

        tenant_id = get_current_tenant_id() or 0
        subject_type = get_current_subject_type() or 0
        subject_id = get_current_subject_id() or "anonymous"

        if cache_type == self.CacheType.DATA:
            # data:{tenant_id}:{resource}:{subject_type}:{subject_id}:{id}
            parts.extend([
                str(tenant_id),
                resource,
                str(subject_type),
                str(subject_id),
            ])
            if key:
                parts.append(key)
            return ":".join(parts)

        if cache_type == self.CacheType.LIST:
            # list:{tenant_id}:{resource}:{action}:{scope}:{subject_type}:{subject_id}:{query_hash}
            parts.extend([
                str(tenant_id),
                resource,
            ])
            if action:
                parts.append(action)
            if scope:
                parts.append(scope)
            parts.extend([
                str(subject_type),
                str(subject_id),
            ])
            if query_params:
                sorted_params = sorted(query_params.items())
                query_str = "&".join([f"{k}={v}" for k, v in sorted_params])
                query_hash = hashlib.md5(query_str.encode("utf-8")).hexdigest()[:8]
                parts.append(query_hash)

        full_key = ":".join(parts)

        if len(full_key) > 250:
            key_hash = hashlib.md5(full_key.encode()).hexdigest()
            full_key = f"{cache_type}:{resource}:{key_hash}"

        return full_key

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
        include_scope: bool = False,
        query_params: Optional[Dict[str, Any]] = None
    ) -> Any | None:
        """
        获取缓存（自动注入权限维度）

        Args:
            cache_type: 缓存类型（GLOBAL/DATA/LIST）
            resource: 资源名称（如goods、order）
            key: 业务层传入的key（单条数据的ID）
            action: 动作名称（列表查询时使用）
            include_scope: 是否包含数据范围（列表查询必须传True）
            query_params: 查询参数（列表查询时使用）

        Returns:
            缓存的值，如果未命中则返回None
        """
        scope = self._get_current_user_scope(resource) if include_scope else None
        full_key = self._build_cache_key(
            cache_type=cache_type,
            resource=resource,
            key=key,
            action=action,
            scope=scope,
            query_params=query_params
        )
        return self._get_raw(full_key)

    def set(
        self,
        cache_type: str,
        resource: str,
        value: Any,
        key: str = None,
        action: str = None,
        include_scope: bool = False,
        query_params: Optional[Dict[str, Any]] = None,
        l1_ttl: int | None = None,
        l2_ttl: int | None = None
    ) -> None:
        """
        设置缓存（自动注入权限维度）

        Args:
            cache_type: 缓存类型（GLOBAL/DATA/LIST）
            resource: 资源名称
            value: 要缓存的值
            key: 业务层传入的key（单条数据的ID）
            action: 动作名称（列表查询时使用）
            include_scope: 是否包含数据范围
            query_params: 查询参数（列表查询时使用）
            l1_ttl: L1缓存过期时间（秒），不传则使用配置默认值
            l2_ttl: L2缓存过期时间（秒），不传则使用配置默认值
        
        TTL 配置建议（从 settings 导入）：
            - HIGH: 高频数据（用户会话、实时数据）
            - MEDIUM: 中频数据（字典数据、配置信息）
            - LOW: 低频数据（系统配置、权限数据）
        """
        scope = self._get_current_user_scope(resource) if include_scope else None
        full_key = self._build_cache_key(
            cache_type=cache_type,
            resource=resource,
            key=key,
            action=action,
            scope=scope,
            query_params=query_params
        )
        self._set_raw(full_key, value, l1_ttl, l2_ttl)

    def delete(
        self,
        cache_type: str,
        resource: str,
        key: str = None,
        action: str = None,
        include_scope: bool = False
    ) -> None:
        """
        删除指定资源的缓存

        Args:
            cache_type: 缓存类型
            resource: 资源名称
            key: 不传则删除该资源下该用户的所有缓存
            action: 动作名称
            include_scope: 是否包含数据范围维度
        """
        scope = self._get_current_user_scope(resource) if include_scope else None

        if key:
            full_key = self._build_cache_key(
                cache_type=cache_type,
                resource=resource,
                key=key,
                action=action,
                scope=scope
            )
            self._delete_raw(full_key)
        else:
            pattern = self._build_cache_key(
                cache_type=cache_type,
                resource=resource,
                key="*",
                action=action,
                scope=scope
            )
            self._clear_pattern_raw(pattern)

    def delete_by_subject(
        self,
        subject_type: int,
        subject_id: int,
        tenant_id: int = None
    ) -> None:
        """
        清除指定主体的所有缓存（权限变更时调用）

        Args:
            subject_type: 主体类型（0=用户，1=成员）
            subject_id: 主体ID
            tenant_id: 租户ID（不传则使用当前上下文的租户ID）
        """
        from src.common.core.context import get_current_tenant_id
        tenant_id = tenant_id or get_current_tenant_id() or 0
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

    def _get_current_user_scope(self, resource: str) -> str:
        """获取当前用户对指定资源的数据范围"""
        from src.common.core.auth.data_permission import get_current_user_scope
        return get_current_user_scope(resource)

    def get_global(self, resource: str, key: str) -> Any | None:
        """获取全局静态缓存"""
        return self.get(
            cache_type=self.CacheType.GLOBAL,
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
        # 默认使用 LOW 级别（最长缓存时间）
        final_l1_ttl = l1_ttl if l1_ttl is not None else settings.L1_CACHE_TTL_LOW
        final_l2_ttl = l2_ttl if l2_ttl is not None else settings.L2_CACHE_TTL_LOW
        
        self.set(
            cache_type=self.CacheType.GLOBAL,
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
        cache_type: str = None
    ) -> Callable:
        """
        装饰器：自动缓存方法返回值

        Args:
            resource: 资源名称（如 user_detail）
            l1_ttl: L1缓存过期时间（秒），不传则使用配置默认值
            l2_ttl: L2缓存过期时间（秒），不传则使用配置默认值
            cache_type: 缓存类型（DATA/LIST/GLOBAL），不传则根据方法参数自动判断

        使用示例：
            @cache_manager.cached("user_detail", l1_ttl=300, l2_ttl=3600)
            def get_user_detail(self, user_id: int) -> dict:
                ...
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                # 生成缓存键：使用方法名 + 参数作为key
                key_parts = [func.__name__]
                
                # 收集位置参数（跳过第一个参数self/cls）
                for i, arg in enumerate(args[1:], 1):
                    if arg is not None:
                        key_parts.append(f"arg{i}_{arg}")
                
                # 收集关键字参数
                for k, v in sorted(kwargs.items()):
                    if v is not None:
                        key_parts.append(f"{k}_{v}")
                
                key = "_".join(key_parts)
                
                # 获取缓存
                final_cache_type = cache_type or self.CacheType.DATA
                cached_result = self.get(
                    cache_type=final_cache_type,
                    resource=resource,
                    key=key
                )
                
                if cached_result is not None:
                    return cached_result
                
                # 调用原方法
                result = func(*args, **kwargs)
                
                # 写入缓存（仅在结果不为None时）
                if result is not None:
                    self.set(
                        cache_type=final_cache_type,
                        resource=resource,
                        key=key,
                        value=result,
                        l1_ttl=l1_ttl,
                        l2_ttl=l2_ttl
                    )
                
                return result
            
            return wrapper
        
        return decorator


cache_manager = CacheManager()


def clear_user_cache(user_id: int) -> None:
    """清除指定用户的所有相关缓存

    Args:
        user_id: 用户 ID
    """
    cache_manager.delete_by_subject(subject_type=0, subject_id=user_id)
