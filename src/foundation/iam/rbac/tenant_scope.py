"""租户隔离作用域

TenantScope 承载租户过滤，
tenant_isolation.py（读方向 before_compile）、
session_events.py（写方向 before_flush）调用本模块。

TenantScope 字段:
  skip:          bool
  filter_mode:   'eq' | 'is_null' | 'skip'
  filter_value:  int | None
  tenant_id:     int | None
  path_tenant_id: int | None
  interface_type: InterfaceType | None
"""

import logging
from dataclasses import dataclass

from src.core.annotations import InterfaceType
from src.foundation.iam.auth.context import get_current_auth_context
from src.foundation.iam.query_context import is_skip_tenant

logger = logging.getLogger(__name__)


@dataclass
class TenantScope:
    skip: bool
    filter_mode: str | None = None
    filter_value: int | None = None
    tenant_id: int | None = None
    path_tenant_id: int | None = None
    interface_type: InterfaceType | None = None

    def cache_suffix(self) -> str:
        if self.skip or self.filter_mode == 'skip':
            return ":tenant:skip"
        if self.filter_mode == 'is_null':
            return ":tenant:null"
        if self.filter_mode == 'eq':
            return f":tenant:{self.filter_value}"
        return ":tenant:skip"


def _resolve_filter_tenant_id(ctx) -> tuple[int | None, str]:
    itype = ctx.interface_type

    if itype == InterfaceType.PUBLIC:
        if ctx.path_tenant_id is not None and ctx.path_tenant_id > 0:
            return ctx.path_tenant_id, 'eq'
        if ctx.path_tenant_id == 0:
            return None, 'is_null'
        return None, 'skip'

    if itype == InterfaceType.PLATFORM:
        return None, 'is_null'

    if itype == InterfaceType.TENANT:
        if ctx.tenant_id is None:
            return None, 'skip'
        return ctx.tenant_id, 'eq'

    if ctx.path_tenant_id is not None and ctx.path_tenant_id > 0:
        return ctx.path_tenant_id, 'eq'
    if ctx.path_tenant_id == 0:
        return None, 'is_null'
    if ctx.tenant_id is not None:
        return ctx.tenant_id, 'eq'
    return None, 'is_null'


def get_tenant_scope_for_read() -> TenantScope:
    try:
        ctx = get_current_auth_context()
        if ctx is None:
            return TenantScope(skip=True)

        if is_skip_tenant():
            return TenantScope(
                skip=True,
                tenant_id=ctx.tenant_id,
                path_tenant_id=ctx.path_tenant_id,
                interface_type=ctx.interface_type,
            )

        filter_value, filter_mode = _resolve_filter_tenant_id(ctx)

        return TenantScope(
            skip=False,
            filter_mode=filter_mode,
            filter_value=filter_value,
            tenant_id=ctx.tenant_id,
            path_tenant_id=ctx.path_tenant_id,
            interface_type=ctx.interface_type,
        )
    except Exception:
        ctx_snapshot = get_current_auth_context()
        logger.error(
            "get_tenant_scope_for_read 异常: interface_type=%s, tenant_id=%s, path_tenant_id=%s",
            getattr(ctx_snapshot, 'interface_type', 'N/A') if ctx_snapshot else 'N/A',
            getattr(ctx_snapshot, 'tenant_id', 'N/A') if ctx_snapshot else 'N/A',
            getattr(ctx_snapshot, 'path_tenant_id', 'N/A') if ctx_snapshot else 'N/A',
            exc_info=True,
        )
        raise


def get_tenant_scope_for_write() -> TenantScope:
    try:
        ctx = get_current_auth_context()
        if ctx is None:
            return TenantScope(skip=True)

        filter_value, filter_mode = _resolve_filter_tenant_id(ctx)

        return TenantScope(
            skip=False,
            filter_mode=filter_mode,
            filter_value=filter_value,
            tenant_id=ctx.tenant_id,
            path_tenant_id=ctx.path_tenant_id,
            interface_type=ctx.interface_type,
        )
    except Exception:
        ctx_snapshot = get_current_auth_context()
        logger.error(
            "get_tenant_scope_for_write 异常: interface_type=%s, tenant_id=%s, path_tenant_id=%s",
            getattr(ctx_snapshot, 'interface_type', 'N/A') if ctx_snapshot else 'N/A',
            getattr(ctx_snapshot, 'tenant_id', 'N/A') if ctx_snapshot else 'N/A',
            getattr(ctx_snapshot, 'path_tenant_id', 'N/A') if ctx_snapshot else 'N/A',
            exc_info=True,
        )
        raise