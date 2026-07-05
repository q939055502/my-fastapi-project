from src.core.annotations import InterfaceType
from src.foundation.iam.rbac.tenant_scope import TenantScope


def _has_column(entity, column_name: str) -> bool:
    return hasattr(entity, column_name)


def fill_tenant_id(instance, tenant_scope: TenantScope) -> bool:
    if not _has_column(instance, 'tenant_id'):
        return False
    if getattr(instance, 'tenant_id', None) is not None:
        return False

    itype = tenant_scope.interface_type
    target_tenant_id = None

    if itype == InterfaceType.PUBLIC:
        pass
    elif itype == InterfaceType.PLATFORM:
        target_tenant_id = None
    elif itype == InterfaceType.TENANT:
        target_tenant_id = tenant_scope.tenant_id
    elif itype == InterfaceType.ALL:
        if tenant_scope.path_tenant_id is not None and tenant_scope.path_tenant_id > 0:
            target_tenant_id = tenant_scope.tenant_id
        elif tenant_scope.path_tenant_id == 0:
            target_tenant_id = None
        else:
            target_tenant_id = None
    else:
        target_tenant_id = None

    if target_tenant_id is None and itype != InterfaceType.PLATFORM:
        return False

    instance.tenant_id = target_tenant_id
    return True