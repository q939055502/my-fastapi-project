"""
RBAC 权限控制包

包含:
- PermissionControl: 权限校验
- invalidate_rbac_cache / invalidate_all_rbac_cache: 缓存失效
- middleware: 中间件
- repository: 角色/权限/关联仓储
- service: 角色/权限服务
- tenant_isolation: 租户隔离 before_compile + before_flush
- login_ctx: 登录上下文缓存 (login_ctx:{user_id})

FastAPI 依赖注入入口 require_auth / require_permission 在
src.foundation.iam.decorators 提供。
"""

from .login_ctx import get_login_ctx, invalidate_login_ctx
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
    "get_login_ctx",
    "invalidate_login_ctx",
]
