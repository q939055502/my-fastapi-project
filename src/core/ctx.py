
"""
请求上下文管理模块
"""

from contextvars import ContextVar
from typing import Optional

CTX_USER_ID: ContextVar[Optional[int]] = ContextVar("user_id", default=None)
CTX_TENANT_ID: ContextVar[Optional[int]] = ContextVar("tenant_id", default=None)
CTX_BG_TASKS: ContextVar[Optional[object]] = ContextVar("bg_tasks", default=None)
CTX_REQUEST_ID: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_current_user_id() -> Optional[int]:
    """获取当前用户ID"""
    return CTX_USER_ID.get()


def set_current_user_id(user_id: int) -> None:
    """设置当前用户ID"""
    CTX_USER_ID.set(user_id)


def get_current_tenant_id() -> Optional[int]:
    """获取当前租户ID"""
    return CTX_TENANT_ID.get()


def set_current_tenant_id(tenant_id: int) -> None:
    """设置当前租户ID"""
    CTX_TENANT_ID.set(tenant_id)


def clear_context() -> None:
    """清空上下文变量"""
    CTX_USER_ID.set(None)
    CTX_TENANT_ID.set(None)
    CTX_BG_TASKS.set(None)
    CTX_REQUEST_ID.set(None)

