"""租户解析工具

提供 tenant_key 到 tenant_id 的解析功能，给中间件使用。
"""

from typing import Optional
from sqlalchemy import text

from src.common.core.storage import cache_manager, SessionLocal
from src.models.tenant.tenant import Tenant


def resolve_tenant_id(tenant_key: str) -> Optional[int]:
    """根据 tenant_key 解析 tenant_id

    Args:
        tenant_key: 租户 key

    Returns:
        tenant_id (int) 或 0 (platform)，没有找到则返回 None
    """
    # 特殊处理 platform
    if tenant_key == "platform":
        return 0

    # 先从缓存取
    cached_tenant_id = cache_manager.get_global(resource="tenant", key=tenant_key)
    if cached_tenant_id is not None:
        return cached_tenant_id if cached_tenant_id != -1 else None

    # 缓存没有，去数据库查
    tenant_id = _query_tenant_id_from_db(tenant_key)

    # 写入缓存（默认使用最长TTL，租户信息不常变化）
    cache_value = tenant_id if tenant_id is not None else -1
    cache_manager.set_global(resource="tenant", key=tenant_key, value=cache_value)

    return tenant_id


def _query_tenant_id_from_db(tenant_key: str) -> Optional[int]:
    """从数据库查询 tenant_id"""
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.code == tenant_key).first()
        return tenant.id if tenant else None
    finally:
        db.close()
