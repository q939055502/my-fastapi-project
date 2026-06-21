"""
IAM (Identity and Access Management) 身份与访问管理

子模块说明:
- auth: 认证(登录, 注册, Token管理, 上下文)
- rbac: 权限(角色, 权限, 权限校验)
- tenant_isolation: 租户隔离(before_compile + before_flush)
- data_permission: 数据权限(数据范围过滤 + 软删除)
- query_context: 查询上下文(控制哪些查询参与租户过滤)

三层架构:
1. 入口层: decorators 提供依赖注入(认证/权限)
2. 业务层: auth 是"认证", rbac 是"权限校验", tenant_isolation 租户过滤, data_permission 数据权限
3. 持久层: repository 提供数据访问

RBAC 说明:
- subject_type=0, subject_id=user_id     平台用户
- subject_type=1, subject_id=member_id  租户成员
- 平台权限校验用户, 租户权限校验成员
"""

from .auth import (
    AuthContext,
    AuthControl,
    InterfaceType,
    create_token_pair,
    get_current_username,
    login_required,
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
