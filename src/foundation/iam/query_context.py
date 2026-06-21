"""
查询上下文标记模块

使用 ContextVar 实现请求级别的查询上下文标记,
供数据权限过滤(before_compile)和其他模块使用。

使用场景:
1. 平台管理员跨租户查询 -> set_query_context(skip_tenant=True)
2. 后台任务/全量导出(跳过所有过滤) -> set_query_context(skip_data_permission=True)
3. 回收站查询 -> set_query_context(skip_soft_delete=True)

与认证上下文(auth/context.py)的区别:
- auth/context.py: 存储认证结果(你是谁), 由 RequestContextMiddleware 写入
- query_context.py: 存储查询控制标记(怎么过滤), 由业务代码显式设置
两者都是 ContextVar, 但职责完全不同。
"""

from contextvars import ContextVar

_QUERY_CONTEXT: ContextVar[dict | None] = ContextVar("query_context", default=None)


def set_query_context(
    skip_tenant: bool = False,
    skip_data_permission: bool = False,
    skip_soft_delete: bool = False,
) -> None:
    """设置当前请求的查询上下文标记"""
    _QUERY_CONTEXT.set({
        "skip_tenant": skip_tenant,
        "skip_data_permission": skip_data_permission,
        "skip_soft_delete": skip_soft_delete,
    })


def get_query_context() -> dict:
    """获取当前请求的查询上下文标记"""
    ctx = _QUERY_CONTEXT.get()
    if ctx is None:
        return {}
    return ctx


def is_skip_tenant() -> bool:
    """是否跳过租户隔离过滤"""
    return get_query_context().get("skip_tenant", False)


def is_skip_data_permission() -> bool:
    """是否跳过所有数据权限过滤"""
    return get_query_context().get("skip_data_permission", False)


def is_skip_soft_delete() -> bool:
    """是否跳过软删除过滤"""
    return get_query_context().get("skip_soft_delete", False)