"""SQLAlchemy Session 事件统一注册

集中注册 before_flush 事件，在单次遍历中完成:
- 填 tenant_id（租户隔离）
- 填 creator_id / updater_id + creator_type / updater_type（用户审计）

creator_type / updater_type 区分身份: 0=平台用户(user_id), 1=租户成员(member_id).
只在字段为 None 时填值，不覆盖业务层显式赋值。
时间戳（created_at/updated_at）由数据库 server_default 自动维护。
"""

from sqlalchemy import event
from sqlalchemy.orm import Session

from src.core.annotations import InterfaceType
from src.foundation.iam.auth.context import get_current_auth_context


IDENTITY_TYPE_PLATFORM = 0
IDENTITY_TYPE_TENANT = 1


def _has_column(entity, column_name):
    return hasattr(entity, column_name)


def _resolve_who(ctx, interface_type):
    """根据接口类型确定写入的身份 ID 和身份类型

    返回 (identity_id, identity_type):
      TENANT 视图 → 存 member_id + IDENTITY_TYPE_TENANT(1)
      其他视图     → 存 user_id  + IDENTITY_TYPE_PLATFORM(0)
    """
    if interface_type == InterfaceType.TENANT and ctx.member_id:
        return ctx.member_id, IDENTITY_TYPE_TENANT
    return ctx.user_id, IDENTITY_TYPE_PLATFORM


def _fill_tenant_id(instance, ctx, interface_type):
    if not _has_column(instance, 'tenant_id'):
        return False
    if getattr(instance, 'tenant_id', None) is not None:
        return False

    target_tenant_id = None
    if interface_type == InterfaceType.PUBLIC:
        pass
    elif interface_type == InterfaceType.PLATFORM:
        target_tenant_id = None
    elif interface_type == InterfaceType.TENANT:
        target_tenant_id = ctx.tenant_id if ctx else None
    else:
        target_tenant_id = (ctx.path_tenant_id if ctx else None) or (ctx.tenant_id if ctx else None)

    if target_tenant_id is None and interface_type != InterfaceType.PLATFORM:
        return False

    instance.tenant_id = target_tenant_id
    return True


def _fill_creator(instance, identity_id, identity_type):
    if identity_id is None:
        return False
    if not _has_column(instance, 'creator_id'):
        return False
    if getattr(instance, 'creator_id', None) is not None:
        return False
    instance.creator_id = identity_id
    if _has_column(instance, 'creator_type') and getattr(instance, 'creator_type', None) is None:
        instance.creator_type = identity_type
    return True


def _fill_updater(instance, identity_id, identity_type):
    if identity_id is None:
        return False
    if not _has_column(instance, 'updater_id'):
        return False
    instance.updater_id = identity_id
    if _has_column(instance, 'updater_type'):
        instance.updater_type = identity_type
    return True


@event.listens_for(Session, 'before_flush')
def before_flush(session, flush_context, instances):
    ctx = get_current_auth_context()
    if ctx is None:
        return

    interface_type = ctx.interface_type
    identity_id, identity_type = _resolve_who(ctx, interface_type)

    for instance in session.new:
        _fill_tenant_id(instance, ctx, interface_type)
        _fill_creator(instance, identity_id, identity_type)
        _fill_updater(instance, identity_id, identity_type)

    for instance in session.dirty:
        _fill_updater(instance, identity_id, identity_type)
