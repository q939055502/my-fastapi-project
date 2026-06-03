
"""
认证上下文管理模块
"""

from contextvars import ContextVar

CTX_USER_ID: ContextVar[int | None] = ContextVar("user_id", default=None)
CTX_MEMBER_ID: ContextVar[int | None] = ContextVar("member_id", default=None)
CTX_TENANT_ID: ContextVar[int | None] = ContextVar("tenant_id", default=None)
CTX_BG_TASKS: ContextVar[object | None] = ContextVar("bg_tasks", default=None)# 后台任务这个放这里不合适是，但目前先不要改动
CTX_REQUEST_ID: ContextVar[str | None] = ContextVar("request_id", default=None)


def get_current_user_id() -> int | None:
    """获取当前用户物理ID（内部使用）"""
    return CTX_USER_ID.get()


def set_current_user_id(user_id: int) -> None:
    """设置当前用户物理ID"""
    CTX_USER_ID.set(user_id)


def get_current_member_id() -> int | None:
    """获取当前成员ID（业务使用）"""
    return CTX_MEMBER_ID.get()


def set_current_member_id(member_id: int) -> None:
    """设置当前成员ID"""
    CTX_MEMBER_ID.set(member_id)


def get_current_tenant_id() -> int | None:
    """获取当前租户ID"""
    return CTX_TENANT_ID.get()


def set_current_tenant_id(tenant_id: int) -> None:
    """设置当前租户ID"""
    CTX_TENANT_ID.set(tenant_id)


def clear_context() -> None:
    """清空上下文变量"""
    CTX_USER_ID.set(None)
    CTX_MEMBER_ID.set(None)
    CTX_TENANT_ID.set(None)
    CTX_BG_TASKS.set(None)
    CTX_REQUEST_ID.set(None)
