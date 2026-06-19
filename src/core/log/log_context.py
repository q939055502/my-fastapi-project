"""
上下文变量模块
用于存储和检索当前上下文中的日志上下文

"""

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class LogContext:

    """

    日志上下文类
    Attributes:
        request_id: 请求ID
        tenant_id: 租户户ID
        user_id: 用户ID
        ip: 用户IP地址
        endpoint: 请求路径
        duration: 请求耗时
        business_code: 业务状态

    """

    request_id: str = "-"
    tenant_id: str = "0"
    user_id: str = "0"
    ip: str = "unknown"
    endpoint: str = "-"
    duration: str = "0ms"
    business_code: str = "-"


# ContextVar  - 日志上下文
CTX_LOG: ContextVar[LogContext] = ContextVar("log_context")

def set_log_context(context: LogContext) -> None:

    """
    设置当前上下文中的日志上下文对象
    Args:
        context: 日志上下文对象
    """

    CTX_LOG.set(context)

def get_log_context() -> LogContext:

    """
    获取当前上下文中的日志上下文对象
    Returns:
        日志上下文对象
    """

    return CTX_LOG.get(LogContext())

def clear_log_context() -> None:

    """
    清除当前上下文中的日志上下文对象
    """

    CTX_LOG.set(LogContext())

def create_log_context(
    request_id: str = "-",
    tenant_id: int | None = None,
    user_id: int | None = None,
    ip: str = "unknown",
    endpoint: str = "-",
    duration: str = "0ms",
    business_code: str = "-",
) -> LogContext:

    """
    创建日志上下文对象

    Args:
        request_id: 请求ID
        tenant_id: 租户户ID
        user_id: 用户ID
        ip: 用户IP地址
        endpoint: 请求路径
        duration: 请求耗时
        business_code: 业务状态

    Returns:
        LogContext: 日志上下文对象

    """

    return LogContext(
        request_id=request_id,
        tenant_id=str(tenant_id) if tenant_id else "system",
        user_id=str(user_id) if user_id else "0",
        ip=ip,
        endpoint=endpoint,
        duration=duration,
        business_code=business_code,

    )

