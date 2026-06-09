"""
上下文模块

统一管理请求上下文变量，基于 Python ContextVar 实现。
包含：认证上下文、日志上下文、后台任务上下文等。

使用方式：
1. 路由层: get_auth_context(request) 或 Depends(get_auth_context)
2. 其他层: get_current_auth_context(), get_current_user_id(), 等无需参数
"""

from .auth_context import (
    CTX_AUTH,
    AuthContext,
    get_auth_context,
    get_current_auth_context,
    get_current_effective_tenant_id,
    get_current_member_id,
    get_current_path_tenant_id,
    get_current_subject_id,
    get_current_subject_type,
    get_current_tenant_id,
    get_current_user_id,
    is_platform_context,
    is_tenant_context,
    set_auth_context,
)
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
    "CTX_AUTH",
    "set_auth_context",
    "get_auth_context",
    "get_current_auth_context",
    "get_current_user_id",
    "get_current_member_id",
    "get_current_tenant_id",
    "get_current_path_tenant_id",
    "get_current_effective_tenant_id",
    "get_current_subject_type",
    "get_current_subject_id",
    "is_platform_context",
    "is_tenant_context",
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
