"""
IAM (Identity and Access Management) 身份与访问管理模块

统一管理认证和授权:
- auth: 认证模块(登录, 注册, Token管理, 认证上下文)
- rbac: 授权模块(角色管理, 权限管理, 权限校验中间件)
- data_permission: 数据权限过滤(租户隔离, 自动填通用字段)
- query_context: 查询上下文标记(控制数据权限过滤行为)

设计原则:
1. 单向依赖: rbac 依赖 auth(授权依赖认证上下文)
2. 职责分离: auth 负责"你是谁", rbac 负责"你能做什么", data_permission 负责全局兜底租户隔离 + 自动填通用字段
3. 统一导出: 对外提供一致的 API 入口, 保持向后兼容

RBAC 主体模型:
- subject_type=0, subject_id=user_id    → 平台用户身份
- subject_type=1, subject_id=member_id   → 租户成员身份
- 权限校验时两层身份都查, 权限码并集去重
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
]
