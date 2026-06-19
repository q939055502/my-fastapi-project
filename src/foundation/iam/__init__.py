"""
IAM (Identity and Access Management) 身份与访问管理模块
统一管理认证和授权:
- auth: 认证模块(登录, 注册, Token管理, 认证上下文)
- rbac: 授权模块(角色管理, 权限管理, 数据权限, 权限校验中间件)
设计原则:
1. 单向依赖:rbac 依赖 auth(授权依赖认证上下文)
2. 职责分离:auth 负责"你是谁",rbac 负责"你能做什么"
3. 统一导出:对外提供一致的 API 入口,保持向后兼容
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
from .rbac import (
    AuthMiddleware,
    PermissionControl,
    PermissionService,
    RoleService,
    apply_scope_filter,
    auth_middleware,
    get_scope_for_resource,
    permission_repository,
    permission_service,
    role_permission_repository,
    role_repository,
    role_service,
    role_subject_repository,
)

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
