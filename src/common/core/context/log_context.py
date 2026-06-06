"""
日志上下文管理模块

提供日志上下文的设置和获取功能，基于 Python ContextVar 实现
支持在异步环境中自动隔离上下文
"""

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass
class LogContext:
    """日志上下文对象

    用于存储请求相关的上下文信息，使日志能够追踪请求链路

    Attributes:
        request_id: 请求追踪ID
        tenant_id: 租户ID
        user_id: 用户ID
        ip: 客户端IP地址
        endpoint: 请求接口路径
        duration: 请求耗时
        business_code: 业务状态码
    """
    request_id: str = "-"
    tenant_id: str = "system"
    user_id: str = "0"
    ip: str = "unknown"
    endpoint: str = "-"
    duration: str = "0ms"
    business_code: str = "-"


# ContextVar 定义 - 自动协程隔离
CTX_LOG: ContextVar[LogContext] = ContextVar("log_context")


def set_log_context(context: LogContext) -> None:
    """设置当前协程的日志上下文

    Args:
        context: 日志上下文对象
    """
    CTX_LOG.set(context)


def get_log_context() -> LogContext:
    """获取当前协程的日志上下文

    Returns:
        LogContext: 当前日志上下文，默认为空上下文
    """
    return CTX_LOG.get(LogContext())


def clear_log_context() -> None:
    """清空日志上下文"""
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
    """便捷函数：创建日志上下文

    Args:
        request_id: 请求追踪ID
        tenant_id: 租户ID（整数，会转为字符串）
        user_id: 用户ID（整数，会转为字符串）
        ip: 客户端IP地址
        endpoint: 请求接口路径
        duration: 请求耗时
        business_code: 业务状态码

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
