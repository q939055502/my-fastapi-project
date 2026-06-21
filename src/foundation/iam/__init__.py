"""
IAM (Identity and Access Management) ?????????

?????????:
- auth: ????(??, ??, Token??, ?????)
- rbac: ????(????, ????, ???????)
- tenant_isolation: ????(before_compile + before_flush)
- data_permission: ???????? + ??????
- query_context: ???????(??????????)

????:
1. ????: rbac ?? auth(?????????)
2. ????: auth ??"???", rbac ??"?????", tenant_isolation ??????, data_permission ?????? + ????
3. ????: ??????? API ??, ??????

RBAC ????:
- subject_type=0, subject_id=user_id     ??????
- subject_type=1, subject_id=member_id    ??????
- ???????????, ???????
"""

from .auth import (
    AuthContext,
    AuthControl,
    InterfaceType,
    create_token_pair,
    get_current_username,
    login_required,
    public_api,
    token_manager,
    verify_token,
)
from .decorators import require_auth, require_permission
from .query_context import (
    get_query_context,
    is_skip_data_permission,
    is_skip_soft_delete,
    is_skip_tenant,
    set_query_context,
)
from .rbac import (
    AuthMiddleware,
    PermissionControl,
    PermissionService,
    RoleService,
    auth_middleware,
    invalidate_all_rbac_cache,
    invalidate_rbac_cache,
    permission_repository,
    permission_service,
    role_permission_repository,
    role_repository,
    role_service,
    role_subject_repository,
)
from .rbac.tenant_isolation import apply_tenant_isolation
from .rbac.data_permission import (
    apply_scope_filter,
    get_scope_for_resource,
)
from .rbac.session_events import before_flush

__all__ = [
    "AuthControl",
    "AuthContext",
    "create_token_pair",
    "get_current_username",
    "verify_token",
    "token_manager",
    "public_api",
    "login_required",
    "InterfaceType",
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
    "require_auth",
    "require_permission",
    "set_query_context",
    "get_query_context",
    "is_skip_tenant",
    "is_skip_data_permission",
    "is_skip_soft_delete",
    "invalidate_rbac_cache",
    "invalidate_all_rbac_cache",
    "apply_tenant_isolation",
    "apply_scope_filter",
    "get_scope_for_resource",
]
