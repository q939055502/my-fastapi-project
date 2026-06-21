"""
认证上下文模块
采用 FastAPI 原生方案:中间件 + 依赖注入
同时支持 ContextVar,在任何地方都能获取上下文
使用方式:1. 路由中 get_auth_context(request) 或 Depends(get_auth_context)
2. 其他地方 get_current_auth_context()  # 无需参数
"""

from contextvars import ContextVar
from dataclasses import dataclass

from fastapi import Request

CTX_AUTH: ContextVar["AuthContext | None"] = ContextVar("auth_context", default=None)


@dataclass
class AuthContext:
    """认证上下文

    request_id: 请求追踪 ID
    user_id: 平台用户表 ID（平台视图时为 null 说明未登录或公共接口）
    username: 用户名
    tenant_id: 当前选中的租户 ID（平台视图时为 null）
    path_tenant_id: 请求路径里指定的租户 ID（跨租户操作时）
    member_id: 当前 tenant_id 对应的成员 subject_id（平台视图时为 null）
    client_ip: 请求来源 IP
    """
    request_id: str = "-"
    user_id: int | None = None
    username: str = ""
    tenant_id: int | None = None
    path_tenant_id: int | None = None
    member_id: int | None = None
    client_ip: str = "unknown"


def set_auth_context(context: AuthContext) -> None:
    CTX_AUTH.set(context)


def get_current_auth_context() -> AuthContext | None:
    return CTX_AUTH.get()


def get_auth_context(request: Request) -> AuthContext:
    if not hasattr(request.state, "auth_context"):
        raise RuntimeError(
            "AuthContext not found. Make sure RequestContextMiddleware is added to the app."
        )
    return request.state.auth_context


def _ctx() -> AuthContext | None:
    return CTX_AUTH.get()


def get_current_user_id() -> int | None:
    ctx = _ctx()
    return ctx.user_id if ctx else None


def get_current_member_id() -> int | None:
    ctx = _ctx()
    return ctx.member_id if ctx else None


def get_current_tenant_id() -> int | None:
    ctx = _ctx()
    return ctx.tenant_id if ctx else None


def get_current_path_tenant_id() -> int | None:
    ctx = _ctx()
    return ctx.path_tenant_id if ctx else None


def get_current_client_ip(request: Request = None) -> str:
    if request:
        ctx = get_auth_context(request)
    else:
        ctx = get_current_auth_context()
    return ctx.client_ip if ctx else "unknown"
