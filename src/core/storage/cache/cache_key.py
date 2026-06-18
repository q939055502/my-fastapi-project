"""缓存键构建器（核心层）

提供通用的缓存键构建功能，不依赖任何业务逻辑。
业务维度的注入由 foundation 层负责。

缓存键分层设计：
    - GLOBAL: global:{resource}:{key}
    - DATA: data:{tenant_id}:{resource}:{subject_type}:{subject_id}:{id}
    - LIST: list:{tenant_id}:{resource}:{action}:{scope}:{subject_type}:{subject_id}:{query_hash}
"""

import hashlib
from typing import Any, Dict, Optional


class CacheType:
    """缓存类型枚举"""
    GLOBAL = "global"
    DATA = "data"
    LIST = "list"


def build_cache_key(
    cache_type: str,
    resource: str,
    key: Optional[str] = None,
    action: Optional[str] = None,
    scope: Optional[str] = None,
    query_params: Optional[Dict[str, Any]] = None,
    tenant_id: Optional[int] = None,
    subject_type: Optional[int] = None,
    subject_id: Optional[str] = None,
) -> str:
    """
    构建缓存键（显式参数版本）

    Args:
        cache_type: 缓存类型（GLOBAL/DATA/LIST）
        resource: 资源名称
        key: 业务层传入的key（单条数据的ID）
        action: 动作名称（列表查询时使用）
        scope: 数据范围
        query_params: 查询参数（列表查询时使用）
        tenant_id: 租户ID（DATA/LIST类型需要）
        subject_type: 主体类型（DATA/LIST类型需要）
        subject_id: 主体ID（DATA/LIST类型需要）

    Returns:
        构建好的缓存键
    """
    parts = [cache_type]

    if cache_type == CacheType.GLOBAL:
        parts.append(resource)
        if key:
            parts.append(key)
        return ":".join(parts)

    # DATA 和 LIST 类型需要业务维度
    parts.extend([
        str(tenant_id or 0),
        resource,
    ])

    if cache_type == CacheType.DATA:
        parts.extend([
            str(subject_type or 0),
            str(subject_id or "anonymous"),
        ])
        if key:
            parts.append(key)
        return ":".join(parts)

    if cache_type == CacheType.LIST:
        if action:
            parts.append(action)
        if scope:
            parts.append(scope)
        parts.extend([
            str(subject_type or 0),
            str(subject_id or "anonymous"),
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