"""
认证上下文模块

采用 FastAPI 原生方案：中间件 + 依赖注入
同时支持 ContextVar，在任何地方都能获取上下文

使用方式：
1. 路由层: get_auth_context(request) 或 Depends(get_auth_context)
2. 其他层: get_current_auth_context()  # 无需参数
"""

from contextvars import ContextVar
from dataclasses import dataclass

from fastapi import Request

# ContextVar 定义 - 中间件设置，其他层读取
CTX_AUTH: ContextVar["AuthContext | None"] = ContextVar("auth_context", default=None)


@dataclass
class AuthContext:
    """认证上下文对象"""
    request_id: str = "-"
    user_id: int | None = None
    username: str = ""
    tenant_id: int | None = None  # 认证租户ID（从JWT来）
    path_tenant_id: int | None = None  # 路径租户ID（从URL来）
    member_id: int | None = None
    client_ip: str = "unknown"
    subject_type: int = 0  # 0=平台用户，1=租户成员
    subject_id: int | None = None  # 当前主体ID（user_id或member_id）

    @property
    def is_platform_user(self) -> bool:
        """是否平台用户"""
        return self.subject_type == 0

    @property
    def is_tenant_user(self) -> bool:
        """是否租户用户"""
        return self.subject_type == 1

    @property
    def effective_tenant_id(self) -> int | None:
        """获取生效的租户ID（路径租户优先，否则用认证租户）"""
        return self.path_tenant_id or self.tenant_id


def set_auth_context(context: AuthContext) -> None:
    """设置认证上下文到 ContextVar（中间件调用）"""
    CTX_AUTH.set(context)


def get_current_auth_context() -> AuthContext | None:
    """获取当前认证上下文（无需 request 参数）

    Returns:
        AuthContext | None: 认证上下文对象，未设置时返回 None
    """
    return CTX_AUTH.get()


def get_auth_context(request: Request) -> AuthContext:
    """获取认证上下文（依赖注入 / request 参数）

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
# 无需 request 参数，从 ContextVar 获取
# 这些函数适合在 repository/service 等非路由层使用

def _ctx() -> AuthContext | None:
    """内部工具：获取上下文"""
    return CTX_AUTH.get()


def get_current_user_id() -> int | None:
    """获取当前用户物理ID"""
    ctx = _ctx()
    return ctx.user_id if ctx else None


def get_current_member_id() -> int | None:
    """获取当前成员ID"""
    ctx = _ctx()
    return ctx.member_id if ctx else None


def get_current_tenant_id() -> int | None:
    """获取当前租户ID（认证租户）"""
    ctx = _ctx()
    return ctx.tenant_id if ctx else None


def get_current_path_tenant_id() -> int | None:
    """获取路径租户ID"""
    ctx = _ctx()
    return ctx.path_tenant_id if ctx else None


def get_current_effective_tenant_id() -> int | None:
    """获取生效的租户ID（路径租户优先）"""
    ctx = _ctx()
    return ctx.effective_tenant_id if ctx else None


def get_current_subject_type() -> int:
    """获取当前主体类型（0=平台用户，1=租户成员）"""
    ctx = _ctx()
    return ctx.subject_type if ctx else 0


def get_current_subject_id() -> int | None:
    """获取当前主体ID（user_id或member_id）"""
    ctx = _ctx()
    return ctx.subject_id if ctx else None


def is_platform_context() -> bool:
    """是否平台上下文（平台用户且无路径租户）"""
    ctx = _ctx()
    if not ctx:
        return False
    return ctx.is_platform_user and ctx.path_tenant_id is None


def is_tenant_context() -> bool:
    """是否租户上下文"""
    ctx = _ctx()
    if not ctx:
        return False
    return ctx.is_tenant_user or ctx.path_tenant_id is not None


def get_current_client_ip(request: Request = None) -> str:
    """获取当前客户端IP

    支持两种调用方式：
    1. 路由层：get_current_client_ip(request) - 从 request.state 获取
    2. 其他层：get_current_client_ip() - 从 ContextVar 获取

    Args:
        request: FastAPI 请求对象（可选）

    Returns:
        str: 客户端IP地址
    """
    if request:
        ctx = get_auth_context(request)
    else:
        ctx = get_current_auth_context()

    return ctx.client_ip if ctx else "unknown"
