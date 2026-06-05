"""
上下文模块

统一管理请求上下文变量，基于 Python ContextVar 实现。
包含：认证上下文、日志上下文、后台任务上下文等。
"""

from .auth_context import AuthContext, get_auth_context
from .bgtask_context import CTX_BG_TASKS, clear_bg_tasks, get_bg_tasks, set_bg_tasks
from .log_context import (
    CTX_LOG,
    LogContext,
    clear_log_context,
    create_log_context,
    get_log_context,
    set_log_context,
)

__all__ = [
    # 认证上下文
    "AuthContext",
    "get_auth_context",
    # 日志上下文
    "LogContext",
    "CTX_LOG",
    "get_log_context",
    "set_log_context",
    "clear_log_context",
    "create_log_context",
    # 后台任务上下文
    "CTX_BG_TASKS",
    "get_bg_tasks",
    "set_bg_tasks",
    "clear_bg_tasks",
]
