"""
RBAC ????????

??:
- PermissionControl: ???????
- invalidate_rbac_cache / invalidate_all_rbac_cache: ????
- middleware: ???????
- repository: ??/??/?????????
- service: ??/?????????????
- tenant_isolation: ?????before_compile + before_flush?

FastAPI ?????require_auth / require_permission????
src.foundation.iam.decorators ???
"""

from .middleware import AuthMiddleware, auth_middleware
from .permission_control import (
    PermissionControl,
    invalidate_all_rbac_cache,
    invalidate_rbac_cache,
)
from .repository import (
    permission_repository,
    role_permission_repository,
    role_repository,
    role_subject_repository,
)
from .service import PermissionService, RoleService, permission_service, role_service
from .tenant_isolation import apply_tenant_isolation

__all__ = [
    "PermissionControl",
    "AuthMiddleware",
    "auth_middleware",
    "RoleService",
    "role_service",
    "PermissionService",
    "permission_service",
    "role_repository",
    "permission_repository",
    "role_permission_repository",
    "role_subject_repository",
    "invalidate_rbac_cache",
    "invalidate_all_rbac_cache",
    "apply_tenant_isolation",
]
