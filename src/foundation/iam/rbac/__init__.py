"""
RBAC 角色权限管理模块

包含- 角色管理(平台角色和租户角色)
- 权限管理(菜单按钮/API权限)
- 角色权限关联
- 角色主体关联(用户成员与角色的关联)
- 权限检查执行器(PermissionControl)
- 权限校验中间件(AuthMiddleware)
- 数据权限过滤(租户隔离 + 数据范围)
"""

from .data_permission import (
    apply_scope_filter,
    get_scope_for_resource,
)
from .dependency import PermissionControl
from .middleware import AuthMiddleware, auth_middleware
from .repository import (
    permission_repository,
    role_permission_repository,
    role_repository,
    role_subject_repository,
)
from .service import PermissionService, RoleService, permission_service, role_service

__all__ = [
    "PermissionControl",
    "AuthMiddleware",
    "auth_middleware",
    "apply_scope_filter",
    "get_scope_for_resource",
    "RoleService",
    "role_service",
    "PermissionService",
    "permission_service",
    "role_repository",
    "permission_repository",
    "role_permission_repository",
    "role_subject_repository",
]
