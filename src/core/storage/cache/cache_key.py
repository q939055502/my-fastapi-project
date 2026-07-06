"""缓存键构建器(核心层)

提供通用的缓存键构建功能,不依赖任何业务逻辑。

缓存键分层设计(tag_hash 嵌入,标签版本变化即全换):
    - GLOBAL: global:{tag_hash}:{resource}:{key}
    - DATA:   data:{tag_hash}:{tenant_id}:{resource}:{key}
    - LIST:   list:{tag_hash}:{tenant_id}:{resource}:{query_hash}

tag_hash 由 TagStore.calc_tag_hash 计算,任一标签版本变化后
下一次 build_cache_key 会拿到新的 tag_hash,旧键自然过期。

注意:
    - tenant_id 保留用于租户隔离(不同租户数据物理隔离)
    - 数据范围过滤由业务层(Service)负责,不在缓存键中体现
"""

import hashlib
from typing import Any


class CacheType:
    """缓存类型枚举"""
    GLOBAL = "global"
    DATA = "data"
    LIST = "list"


def build_cache_key(
    cache_type: str,
    resource: str,
    key: str | None = None,
    query_params: dict[str, Any] | None = None,
    tenant_id: int | None = None,
    tag_hash: str = "v0",
) -> str:
    """构建缓存键

    Args:
        cache_type: 缓存类型(GLOBAL/DATA/LIST)
        resource: 资源名称
        key: 数据主键或业务key(单条数据使用)
        query_params: 查询参数(列表查询时使用)
        tenant_id: 租户ID(DATA/LIST类型需要)
        tag_hash: 标签版本哈希,由 TagStore.calc_tag_hash 计算

    Returns:
        构建好的缓存键
    """
    parts = [cache_type, tag_hash]

    if cache_type == CacheType.GLOBAL:
        parts.append(resource)
        if key:
            parts.append(key)
        return ":".join(parts)

    parts.extend([
        str(tenant_id or 0),
        resource,
    ])

    if cache_type == CacheType.DATA:
        if key:
            parts.append(key)
        return ":".join(parts)

    if cache_type == CacheType.LIST:
        if query_params:
            sorted_params = sorted(query_params.items())
            query_str = "&".join([f"{k}={v}" for k, v in sorted_params])
            query_hash = hashlib.md5(query_str.encode("utf-8")).hexdigest()[:8]
            parts.append(query_hash)

    full_key = ":".join(parts)

    if len(full_key) > 250:
        key_hash = hashlib.md5(full_key.encode()).hexdigest()
        full_key = f"{cache_type}:{tag_hash}:{resource}:{key_hash}"

    return full_key
