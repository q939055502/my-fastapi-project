from contextvars import ContextVar
from dataclasses import dataclass
from typing import Optional

from fastapi import Request

from src.core.annotations import InterfaceType

CTX_AUTH: ContextVar['AuthContext | None'] = ContextVar('auth_context', default=None)


@dataclass
class AuthContext:
    request_id: str = '-'
    user_id: Optional[int] = None
    username: str = ''
    tenant_id: Optional[int] = None
    path_tenant_id: Optional[int] = None
    member_id: Optional[int] = None
    active_org_root_id: Optional[int] = None
    active_org_ids: Optional[list[int]] = None
    client_ip: str = 'unknown'
    interface_type: Optional[InterfaceType] = None


def set_auth_context(context: AuthContext) -> None:
    CTX_AUTH.set(context)


def get_current_auth_context() -> Optional[AuthContext]:
    return CTX_AUTH.get()


def get_auth_context(request: Request) -> AuthContext:
    if not hasattr(request.state, 'auth_context'):
        raise RuntimeError('AuthContext not found. Make sure RequestContextMiddleware is added to the app.')
    return request.state.auth_context


def _ctx() -> Optional[AuthContext]:
    return CTX_AUTH.get()


def get_current_user_id() -> Optional[int]:
    ctx = _ctx()
    return ctx.user_id if ctx else None


def get_current_member_id() -> Optional[int]:
    ctx = _ctx()
    return ctx.member_id if ctx else None


def get_current_tenant_id() -> Optional[int]:
    ctx = _ctx()
    return ctx.tenant_id if ctx else None


def get_current_path_tenant_id() -> Optional[int]:
    ctx = _ctx()
    return ctx.path_tenant_id if ctx else None


def get_current_client_ip(request: Optional[Request] = None) -> str:
    if request:
        ctx = get_auth_context(request)
    else:
        ctx = get_current_auth_context()
    return ctx.client_ip if ctx else 'unknown'
