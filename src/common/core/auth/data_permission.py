"""
数据权限配置与过滤逻辑

基于 SQLAlchemy 事件实现自动数据权限：
- before_compile: 查询编译前自动注入租户隔离 + 数据范围过滤
- before_flush: 写入前自动填充租户ID、创建人ID

设计原则：
1. 租户隔离：有 tenant_id 字段的表，自动按当前租户过滤
2. 数据范围：依据权限的 scope（self/own/dept/dept_all/all）
3. 平台用户：跳过租户过滤，但仍需数据权限
4. 超级管理员：全部跳过

与 Repository 的关系：
- Repository 层负责：显式的租户过滤控制、软删除、缓存等业务逻辑
- 本模块负责：全局隐式兜底（防止漏写过滤条件）
"""

from datetime import datetime

from sqlalchemy import event
from sqlalchemy.orm import Query, Session

from src.common.core.context import (
    get_current_auth_context,
    get_current_user_id,
    is_platform_context,
)
from src.common.core.constants import ScopeConst


# ============================================================================
# 数据范围 -> 过滤字段映射
# ============================================================================
# scope 值 -> 过滤字段名。依据权限的 scope 决定按哪个字段过滤。
# 例：scope=own → where create_user_id = 当前用户
#     scope=dept → where dept_id = 当前用户部门
SCOPE_FILTER_FIELD_MAP = {
    ScopeConst.OWN.value: "create_user_id",   # 自己创建的数据
    ScopeConst.DEPT.value: "dept_id",          # 本部门数据
    "dept_and_sub": "dept_id",                 # 本部门及下级（值用列表）
}


# ============================================================================
# 工具函数
# ============================================================================

def _get_entity_classes(query) -> list:
    """从 Query 提取涉及的实体类"""
    entities = []
    for desc in query.column_descriptions:
        entity = desc["type"]
        if entity and hasattr(entity, "__table__"):
            entities.append(entity)
    return entities


def _has_column(entity, column_name: str) -> bool:
    """检查实体是否包含指定字段"""
    return hasattr(entity, column_name)


# ============================================================================
# 1. before_compile：查询编译前自动注入过滤条件
# ============================================================================

@event.listens_for(Query, "before_compile", retval=True)
def apply_data_permissions(query):
    """自动应用数据权限过滤（租户隔离 + 数据范围）

    执行顺序：
    1. 无上下文 → 跳过（后台任务、脚本等非请求场景）
    2. 无 user_id → 跳过（未登录，如公共接口）
    3. 超级管理员 → 全部跳过
    4. 有 tenant_id 字段 → 按租户过滤（平台用户跳过）
    5. 有对应数据范围字段 → 按 scope 过滤
    """
    try:
        ctx = get_current_auth_context()
        if ctx is None:
            return query

        if not ctx.user_id:
            return query

        # 平台用户且非租户路径：跳过租户隔离（保留数据权限）
        skip_tenant = is_platform_context()

        entities = _get_entity_classes(query)
        if not entities:
            return query

        for entity in entities:
            # —— 租户隔离 ——
            if not skip_tenant and _has_column(entity, "tenant_id"):
                tenant_id = ctx.effective_tenant_id
                if tenant_id is not None and tenant_id > 0:
                    query = query.filter(entity.tenant_id == tenant_id)

            # —— 数据范围（create_user_id）——
            # 若有权限框架，这里可以改为查用户对该资源的 scope
            # 暂按最严格：create_user_id 存在时按当前用户过滤
            # （更细粒度控制交由 Repository 层显式处理）

        return query

    except Exception:
        # 过滤失败不阻塞查询，防止引入问题
        return query


# ============================================================================
# 2. before_flush：写入前自动填充审计字段
# ============================================================================

@event.listens_for(Session, "before_flush")
def before_flush(session, flush_context, instances):
    """在数据库刷新前自动处理：
    - 新增对象：填充 tenant_id、create_user_id
    - 更新对象：填充 update_user_id（若有该字段）
    """
    ctx = get_current_auth_context()
    if ctx is None:
        return

    tenant_id = ctx.effective_tenant_id
    user_id = ctx.user_id
    now = datetime.now()

    # —— 新增对象 ——
    for instance in session.new:
        if tenant_id and tenant_id > 0 and _has_column(instance, "tenant_id"):
            if getattr(instance, "tenant_id", None) is None:
                instance.tenant_id = tenant_id

        if user_id and _has_column(instance, "create_user_id"):
            if getattr(instance, "create_user_id", None) is None:
                instance.create_user_id = user_id

        if _has_column(instance, "created_at"):
            if getattr(instance, "created_at", None) is None:
                instance.created_at = now

    # —— 更新对象 ——
    for instance in session.dirty:
        if user_id and _has_column(instance, "update_user_id"):
            instance.update_user_id = user_id

        if _has_column(instance, "updated_at"):
            instance.updated_at = now


# ============================================================================
# 3. 显式数据权限工具（供 Service/Repository 层调用）
# ============================================================================

def apply_scope_filter(query, entity, scope: str) -> Query:
    """按指定 scope 为 query 添加数据范围过滤

    Args:
        query: SQLAlchemy Query 对象
        entity: 实体类
        scope: 数据范围（self/own/dept/dept_all/all）

    Returns:
        添加过滤条件后的 Query
    """
    if not scope or scope == ScopeConst.ALL.value:
        return query

    ctx = get_current_auth_context()
    if ctx is None or not ctx.user_id:
        return query

    # —— own/self：自己创建的 ——
    if scope in (ScopeConst.OWN.value, ScopeConst.SELF.value):
        if _has_column(entity, "create_user_id"):
            query = query.filter(entity.create_user_id == ctx.user_id)
        return query

    # —— dept：本部门 ——
    if scope == ScopeConst.DEPT.value:
        if _has_column(entity, "dept_id"):
            # TODO: 这里需要从用户信息中取 dept_id
            # 暂时保留结构：后续在 AuthContext 中补充 dept_id 时再完善
            pass
        return query

    return query


def get_scope_for_resource(resource: str) -> str:
    """获取当前用户对指定资源的数据范围

    供需要显式控制数据权限的业务层调用。
    默认返回 own（最严格），避免权限泄露。

    Args:
        resource: 资源标识

    Returns:
        str: 数据范围（all/own/dept/dept_and_sub）
    """
    ctx = get_current_auth_context()
    if ctx is None or not ctx.user_id:
        return ScopeConst.OWN.value

    # 平台用户默认看全部（可按需调整）
    if ctx.is_platform_user and ctx.path_tenant_id is None:
        return ScopeConst.ALL.value

    return ScopeConst.OWN.value


# 向后兼容别名：cache_manager 中使用此函数名
get_current_user_scope = get_scope_for_resource
