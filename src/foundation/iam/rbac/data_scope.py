"""数据隔离作用域

DataScope 承载 creator/org/role/tree 等数据维度过滤。
目前仅提供占位默认实现（creator 维度 eq 当前 user）。
以后扩展 tree 模式时在此处落地闭包表查询 + org_id 列表。

DataScope 字段:
  skip:           bool
  dimension_type: 'creator' | 'org' | 'role' | 'custom' | None
  match_type:     'eq' | 'in' | 'all' | 'tree' | None
  dimension_value: str | list[int] | None
"""

import logging
from dataclasses import dataclass

from src.foundation.iam.auth.context import get_current_auth_context
from src.foundation.iam.query_context import is_skip_data_permission

logger = logging.getLogger(__name__)


@dataclass
class DataScope:
    skip: bool
    dimension_type: str | None = None
    match_type: str | None = None
    dimension_value: str | list[int] | None = None

    def cache_suffix(self) -> str:
        if self.skip or self.dimension_type is None:
            return ":data:skip"
        return f":data:{self.dimension_type}:{self.match_type or 'skip'}:{self.dimension_value or ''}"


def get_data_scope_for_read() -> DataScope:
    try:
        if is_skip_data_permission():
            return DataScope(skip=True)

        ctx = get_current_auth_context()
        if ctx is None or ctx.user_id is None:
            return DataScope(skip=True)

        return DataScope(
            skip=False,
            dimension_type='creator',
            match_type='eq',
            dimension_value=str(ctx.user_id),
        )
    except Exception:
        ctx_snapshot = get_current_auth_context()
        logger.error(
            "get_data_scope_for_read 异常: tenant_id=%s, user_id=%s, interface_type=%s",
            getattr(ctx_snapshot, 'tenant_id', 'N/A') if ctx_snapshot else 'N/A',
            getattr(ctx_snapshot, 'user_id', 'N/A') if ctx_snapshot else 'N/A',
            getattr(ctx_snapshot, 'interface_type', 'N/A') if ctx_snapshot else 'N/A',
            exc_info=True,
        )
        raise


def get_data_scope_for_write() -> DataScope:
    """写方向:新创建资源时应该归属哪个组织节点"""
    try:
        if is_skip_data_permission():
            return DataScope(skip=True)

        ctx = get_current_auth_context()
        if ctx is None or ctx.user_id is None:
            return DataScope(skip=True)

        org_ids = ctx.active_org_ids
        if not org_ids:
            return DataScope(skip=True)

        if len(org_ids) == 1:
            return DataScope(
                skip=False,
                dimension_type='org',
                match_type='eq',
                dimension_value=str(org_ids[0]),
            )

        return DataScope(
            skip=False,
            dimension_type='org',
            match_type='in',
            dimension_value=org_ids,
        )
    except Exception:
        ctx_snapshot = get_current_auth_context()
        logger.error(
            "get_data_scope_for_write 异常: tenant_id=%s, user_id=%s, interface_type=%s, active_org_ids=%s",
            getattr(ctx_snapshot, 'tenant_id', 'N/A') if ctx_snapshot else 'N/A',
            getattr(ctx_snapshot, 'user_id', 'N/A') if ctx_snapshot else 'N/A',
            getattr(ctx_snapshot, 'interface_type', 'N/A') if ctx_snapshot else 'N/A',
            getattr(ctx_snapshot, 'active_org_ids', 'N/A') if ctx_snapshot else 'N/A',
            exc_info=True,
        )
        raise
