"""
租户隔离模块

通过 SQLAlchemy 事件监听，自动对所有 ORM 查询施加租户隔离。

核心机制:
- before_compile:  所有 SELECT/UPDATE/DELETE 查询在编译前被拦截，
  自动加上 tenant_id 过滤条件，实现租户间数据隔离。
  实体没有 tenant_id 字段 → 自动跳过（字典、平台表等不参与分租的资源）。
  Tenant 表自身不会参与过滤，因为它没有 tenant_id 字段。

写入时自动填充 tenant_id / creator_id / updater_id 的 before_flush 事件
已集中迁移到 session_events.py。

过滤逻辑由 AuthContext.interface_type（接口类型）决定:
  PUBLIC:   path_tenant_id 有值 → 过滤 path_tenant_id；没有 → skip
  PLATFORM: 过滤 tenant_id IS NULL（只查平台数据）
  TENANT:   过滤 tenant_id = ctx.tenant_id（必须已选租户，从 JWT 来）
  ALL:      path_tenant_id 优先 → tenant_id → 都没有则过滤 NULL（平台视图）

两层可整体跳过:
  query_context.is_skip_data_permission() → 彻底跳过本模块（事务回调等内部调用）
  query_context.is_skip_tenant()         → 跳过租户过滤（平台管理跨租户操作，需额外 RBAC 保护）

注意: 本模块跟登录无关，公开接口也能走过滤（靠 path_tenant_id 过滤）。
"""

from sqlalchemy import event
from sqlalchemy.orm import Query

from src.core.annotations import InterfaceType


def _get_entity_classes(query):
    """从 SQLAlchemy Query 中取出所有涉及的 ORM 实体类"""
    entities = []
    for desc in query.column_descriptions:
        entity = desc['type']
        if entity and hasattr(entity, '__table__'):
            entities.append(entity)
    return entities


def _has_column(entity, column_name):
    """判断实体类是否有指定 ORM 映射字段（允许是模型实例或类本身）"""
    return hasattr(entity, column_name)


def _resolve_filter_tenant_id(ctx):
    """按接口类型确定最终过滤条件

    返回 (filter_value, filter_mode):
      filter_value: int 或 None（int=具体租户id；None 值代表平台数据 tenant_id IS NULL）
      filter_mode:  'eq' | 'is_null' | 'skip'
                    eq      → WHERE tenant_id = filter_value
                    is_null → WHERE tenant_id IS NULL
                    skip    → 不加租户过滤（公开接口无租户上下文时等）
    """
    itype = ctx.interface_type

    if itype == InterfaceType.PUBLIC:
        if ctx.path_tenant_id is not None:
            return ctx.path_tenant_id, 'eq'
        return None, 'skip'

    if itype == InterfaceType.PLATFORM:
        return None, 'is_null'

    if itype == InterfaceType.TENANT:
        if ctx.tenant_id is None:
            return None, 'is_null'
        return ctx.tenant_id, 'eq'

    if ctx.path_tenant_id is not None:
        return ctx.path_tenant_id, 'eq'
    if ctx.tenant_id is not None:
        return ctx.tenant_id, 'eq'
    return None, 'is_null'


@event.listens_for(Query, 'before_compile', retval=True)
def apply_tenant_isolation(query):
    """SQLAlchemy 查询编译前拦截，自动追加租户隔离条件"""
    from src.foundation.iam.auth.context import get_current_auth_context
    from src.foundation.iam.query_context import is_skip_data_permission, is_skip_tenant

    try:
        if is_skip_data_permission():
            return query

        ctx = get_current_auth_context()
        if ctx is None:
            return query

        if is_skip_tenant():
            return query

        filter_value, filter_mode = _resolve_filter_tenant_id(ctx)
        if filter_mode == 'skip':
            return query

        for entity in _get_entity_classes(query):
            if not _has_column(entity, 'tenant_id'):
                continue

            if filter_mode == 'eq':
                query = query.filter(entity.tenant_id == filter_value)
            elif filter_mode == 'is_null':
                query = query.filter(entity.tenant_id.is_(None))

        return query

    except Exception:
        return query
