"""
认证上下文模�?
采用 FastAPI 原生方案:中间件 + 依赖注入
同时支持 ContextVar,在任何地方都能获取上下�?
使用方式�?1. 路由�? get_auth_context(request) �?Depends(get_auth_context)
2. 其他�? get_current_auth_context()  # 无需参数
"""

from contextvars import ContextVar
from dataclasses import dataclass

from fastapi import Request

CTX_AUTH: ContextVar["AuthContext | None"] = ContextVar("auth_context", default=None)


@dataclass
class AuthContext:
    request_id: str = "-"
    user_id: int | None = None
    username: str = ""
    tenant_id: int | None = None
    path_tenant_id: int | None = None
    member_id: int | None = None
    client_ip: str = "unknown"
    subject_type: int = 0
    subject_id: int | None = None

    @property
    def is_platform_user(self) -> bool:
        return self.subject_type == 0

    @property
    def is_tenant_user(self) -> bool:
        return self.subject_type == 1

    @property
    def effective_tenant_id(self) -> int | None:
        return self.path_tenant_id or self.tenant_id


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


def get_current_effective_tenant_id() -> int | None:
    ctx = _ctx()
    return ctx.effective_tenant_id if ctx else None


def get_current_subject_type() -> int:
    ctx = _ctx()
    return ctx.subject_type if ctx else 0


def get_current_subject_id() -> int | None:
    ctx = _ctx()
    return ctx.subject_id if ctx else None


def is_platform_context() -> bool:
    ctx = _ctx()
    if not ctx:
        return False
    return ctx.is_platform_user and ctx.path_tenant_id is None


def is_tenant_context() -> bool:
    ctx = _ctx()
    if not ctx:
        return False
    return ctx.is_tenant_user or ctx.path_tenant_id is not None


def get_current_client_ip(request: Request = None) -> str:
    if request:
        ctx = get_auth_context(request)
    else:
        ctx = get_current_auth_context()
    return ctx.client_ip if ctx else "unknown"
