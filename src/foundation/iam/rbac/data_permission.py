"""
数据权限范围过滤

职责（和 tenant_isolation.py / session_events.py 区分）:
- 租户隔离（tenant_id 过滤）在 tenant_isolation.py 里做，是最外层的墙，跟登录无关
- 写入时自动填 tenant_id / creator_id / updater_id 的 before_flush 在 session_events.py 里集中注册
- 本模块做"用户维度"的事情:
  1. apply_scope_filter   业务层显式调用，按 ScopeConst 加 SELF/OWN 等范围过滤（需要登录 user_id）
  2. get_scope_for_resource 算默认 scope

前置条件: 本模块所有功能都依赖登录（需要 user_id）。
时间戳字段（created_at/updated_at）由数据库 server_default 自动维护，不在此处处理。
"""

from src.core.constants import ScopeConst


SCOPE_FILTER_FIELD_MAP = {
    ScopeConst.OWN.value: 'creator_id',
}


def _has_column(entity, column_name):
    """判断实体类是否有指定 ORM 映射字段（允许是模型实例或类本身）"""
    return hasattr(entity, column_name)


def apply_scope_filter(query, entity, scope):
    """按 ScopeConst（数据权限范围）追加查询条件

    目前只实现了 OWN/SELF（仅查自己创建的数据），
    DEPT/DEPT_AND_SUB 需要 dept_id + 用户所属部门，后续补。
    依赖登录（需要 user_id）；没登录则跳过。
    """
    from src.core.constants import ScopeConst
    from src.foundation.iam.auth.context import get_current_auth_context

    if not scope or scope == ScopeConst.ALL.value:
        return query

    ctx = get_current_auth_context()
    if ctx is None or not ctx.user_id:
        return query

    if scope in (ScopeConst.OWN.value, ScopeConst.SELF.value):
        if _has_column(entity, 'creator_id'):
            query = query.filter(entity.creator_id == ctx.user_id)
        return query

    if scope == ScopeConst.DEPT.value:
        if _has_column(entity, 'dept_id'):
            pass
        return query

    return query


def get_scope_for_resource(resource):
    """根据当前上下文判断默认数据权限范围

    平台视图（没选租户）时不做范围限制（返回 ALL）。
    租户视图时只看自己（返回 OWN）。
    """
    from src.core.constants import ScopeConst
    from src.foundation.iam.auth.context import get_current_auth_context

    ctx = get_current_auth_context()
    if ctx is None or not ctx.user_id:
        return ScopeConst.OWN.value

    if ctx.tenant_id is None and ctx.path_tenant_id is None:
        return ScopeConst.ALL.value

    return ScopeConst.OWN.value


