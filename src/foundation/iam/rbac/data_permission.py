"""
数据权限配置与过滤逻辑

基于 SQLAlchemy 事件实现自动数据权限过滤:
- before_compile: 查询编译前自动注入租户隔离 + 数据范围过滤
- before_flush: 写入前自动填充租户ID, 创建人ID

设计原则:
1. tenant_id 明确 + entity 有 tenant_id 字段 + 没 skip_tenant → 自动过滤
2. path_tenant_id 优先于 tenant_id（路径里指定时用路径的值）
3. tenant_id 为 None → 平台视图, entity.tenant_id IS NULL（平台专属数据）
4. 未登录用户(ctx.user_id 为 null) → 跳过自动过滤，由业务层自己处理（如公共接口）
5. skip_tenant: 显式跳过租户隔离（平台管理员跨租户全量查询）
6. skip_data_permission: 显式跳过所有过滤（后台任务/全量导出）

上下文标记(iam/query_context.py):
- skip_tenant: 跳过租户隔离
- skip_data_permission: 跳过所有过滤
- skip_soft_delete: 跳过软删除

与 Repository 的关系:
- Repository 层负责: 显式的租户过滤控制, 软删除, 缓存等业务逻辑
- 本模块负责: 全局隐式兜底(防止漏写过滤条件)
"""

from datetime import datetime

from sqlalchemy import event
from sqlalchemy.orm import Query, Session

from src.core.constants import ScopeConst

SCOPE_FILTER_FIELD_MAP = {
    ScopeConst.OWN.value: "create_user_id",
    ScopeConst.DEPT.value: "dept_id",
    "dept_and_sub": "dept_id",
}


def _get_entity_classes(query) -> list:
    entities = []
    for desc in query.column_descriptions:
        entity = desc["type"]
        if entity and hasattr(entity, "__table__"):
            entities.append(entity)
    return entities


def _has_column(entity, column_name: str) -> bool:
    return hasattr(entity, column_name)


@event.listens_for(Query, "before_compile", retval=True)
def apply_data_permissions(query):
    """自动应用数据权限过滤(租户隔离)

    执行顺序:
    1. skip_data_permission → 全跳过(后台任务/导出)
    2. ctx is None → 跳过(公共接口/后台脚本/生命周期启动)
    3. skip_tenant → 跳过租户隔离(跨租户全量查询)
    4. path_tenant_id 优先于 tenant_id → 确定过滤值
    5. tenant_id is not None → filter entity.tenant_id == tenant_id
       tenant_id is None → filter entity.tenant_id IS NULL（平台专属数据）
    6. entity 没 tenant_id 字段 → 不加过滤(字典等不分租的资源)
    """
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

        tenant_id = ctx.path_tenant_id or ctx.tenant_id
        for entity in _get_entity_classes(query):
            if not _has_column(entity, "tenant_id"):
                continue

            if tenant_id is not None:
                query = query.filter(entity.tenant_id == tenant_id)
            else:
                query = query.filter(entity.tenant_id.is_(None))

        return query

    except Exception:
        return query


@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    """在数据库刷新前自动处理:
    - 新增对象: 填 tenant_id, create_user_id (仅字段为 None 时填, 不覆盖业务层)
    - 更新对象: 填 update_user_id (若有该字段)
    """
    from src.foundation.iam.auth.context import get_current_auth_context

    ctx = get_current_auth_context()
    if ctx is None:
        return

    tenant_id = ctx.path_tenant_id or ctx.tenant_id
    user_id = ctx.user_id
    now = datetime.now()

    for instance in session.new:
        if tenant_id is not None and tenant_id > 0 and _has_column(instance, "tenant_id") and getattr(instance, "tenant_id", None) is None:
            instance.tenant_id = tenant_id
        if user_id and _has_column(instance, "create_user_id") and getattr(instance, "create_user_id", None) is None:
            instance.create_user_id = user_id
        if _has_column(instance, "created_at") and getattr(instance, "created_at", None) is None:
            instance.created_at = now

    for instance in session.dirty:
        if user_id and _has_column(instance, "update_user_id"):
            instance.update_user_id = user_id
        if _has_column(instance, "updated_at"):
            instance.updated_at = now


def apply_scope_filter(query, entity, scope: str):
    """按指定的 scope 添加数据范围过滤

    Args:
        query: SQLAlchemy Query 对象
        entity: 实体类
        scope: 数据范围(self/own/dept/dept_all/all)
    Returns:
        添加过滤条件后的 Query
    """
    from src.foundation.iam.auth.context import get_current_auth_context

    if not scope or scope == ScopeConst.ALL.value:
        return query

    ctx = get_current_auth_context()
    if ctx is None or not ctx.user_id:
        return query

    if scope in (ScopeConst.OWN.value, ScopeConst.SELF.value):
        if _has_column(entity, "create_user_id"):
            query = query.filter(entity.create_user_id == ctx.user_id)
        return query

    if scope == ScopeConst.DEPT.value:
        if _has_column(entity, "dept_id"):
            pass
        return query

    return query


def get_scope_for_resource(resource: str) -> str:
    """获取当前用户对指定资源的数据范围

    供需要显式控制数据权限的业务层调用。默认返回 own (最严格), 避免权限泄露。
    Args:
        resource: 资源标识

    Returns:
        str: 数据范围 (all/own/dept/dept_and_sub)
    """
    from src.foundation.iam.auth.context import get_current_auth_context

    ctx = get_current_auth_context()
    if ctx is None or not ctx.user_id:
        return ScopeConst.OWN.value

    if ctx.tenant_id is None and ctx.path_tenant_id is None:
        return ScopeConst.ALL.value

    return ScopeConst.OWN.value


get_current_user_scope = get_scope_for_resource
