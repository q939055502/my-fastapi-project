from src.core.annotations import InterfaceType
from src.foundation.iam.auth.context import get_current_auth_context


IDENTITY_TYPE_PLATFORM = 0
IDENTITY_TYPE_TENANT = 1


def _has_column(entity, column_name: str) -> bool:
    return hasattr(entity, column_name)


def _resolve_identity():
    ctx = get_current_auth_context()
    if ctx is None:
        return None, None

    itype = ctx.interface_type
    if itype == InterfaceType.TENANT:
        if ctx.member_id:
            return ctx.member_id, IDENTITY_TYPE_TENANT
        return ctx.user_id, IDENTITY_TYPE_PLATFORM
    if itype == InterfaceType.ALL:
        if ctx.path_tenant_id is not None and ctx.path_tenant_id > 0:
            return ctx.member_id, IDENTITY_TYPE_TENANT
    return ctx.user_id, IDENTITY_TYPE_PLATFORM


def fill_creator(instance) -> bool:
    identity_id, identity_type = _resolve_identity()
    if identity_id is None:
        return False
    if not _has_column(instance, 'creator_id'):
        return False
    if getattr(instance, 'creator_id', None) is not None:
        return False
    instance.creator_id = identity_id
    if _has_column(instance, 'creator_type') and getattr(instance, 'creator_type', None) is None and identity_type is not None:
        instance.creator_type = identity_type
    return True


def fill_updater(instance) -> bool:
    identity_id, identity_type = _resolve_identity()
    if identity_id is None:
        return False
    if not _has_column(instance, 'updater_id'):
        return False
    instance.updater_id = identity_id
    if _has_column(instance, 'updater_type') and identity_type is not None:
        instance.updater_type = identity_type
    return True