"""
认证上下文模块

采用 FastAPI 原生方案：中间件 + 依赖注入
无需手动 set/clear，依赖注入自动创建和管理
"""

from dataclasses import dataclass

from fastapi import Request


@dataclass
class AuthContext:
    """认证上下文对象"""
    request_id: str = "-"
    user_id: int | None = None
    username: str = ""
    tenant_id: int | None = None
    member_id: int | None = None
    client_ip: str = "unknown"


def get_auth_context(request: Request) -> AuthContext:
    """获取认证上下文（依赖注入）

    通过依赖注入自动获取，无需手动 set/clear

    Args:
        request: FastAPI 请求对象

    Returns:
        AuthContext: 认证上下文对象

    Raises:
        RuntimeError: 如果 RequestContextMiddleware 没有设置上下文
    """
    # 如果没有设置过，抛出异常（快速发现问题）
    if not hasattr(request.state, "auth_context"):
        raise RuntimeError(
            "AuthContext not found. Make sure RequestContextMiddleware is added to the app."
        )

    return request.state.auth_context


# ========== 便捷函数 ==========
# 这些函数让你不用每次都写 Depends(get_auth_context)，
# 直接通过 request 就能获取上下文信息

def get_current_user_id(request: Request) -> int | None:
    """获取当前用户物理ID（内部使用）"""
    ctx = get_auth_context(request)
    return ctx.user_id


def get_current_member_id(request: Request) -> int | None:
    """获取当前成员ID（业务使用）"""
    ctx = get_auth_context(request)
    return ctx.member_id


def get_current_tenant_id(request: Request) -> int | None:
    """获取当前租户ID"""
    ctx = get_auth_context(request)
    return ctx.tenant_id

def get_current_request_id(request: Request) -> str:
    """获取当前请求ID"""
    ctx = get_auth_context(request)
    return ctx.request_id


def get_current_client_ip(request: Request) -> str:
    """获取客户端IP"""
    ctx = get_auth_context(request)
    return ctx.client_ip
