"""
Foundation 核心业务能力层 - 提供支撑整个系统运行的通用核心业务能力
- iam: 身份与访问管理(认证 + 授权)
- tenant: 多租户管理
- system: 系统通用功能

设计原则:
1. 领域驱动:按业务领域划分模块,而非按管理视角
2. 高内聚低耦合:每个模块职责单一
3. 单向依赖:foundation 依赖 core,不反向依赖
4. 分层清晰:基础能力在core,基础业务在foundation,具体业务在 modules
"""

from .iam import (
    AuthContext,
    AuthControl,
    AuthMiddleware,
    InterfaceType,
    PermissionControl,
    apply_scope_filter,
    auth_middleware,
    create_token_pair,
    get_scope_for_resource,
    login_required,
    public_api,
    token_manager,
    verify_token,
)
from .iam.auth.context import get_current_auth_context
from .iam.auth.dependency import get_current_username
from .iam.auth.security import (
    create_access_token,
    create_refresh_token,
    generate_password,
    get_password_hash,
    parse_jwt_token,
    pwd_context,
    verify_password,
)

__all__ = [
    "AuthControl",
    "AuthContext",
    "get_current_auth_context",
    "get_current_username",
    "AuthMiddleware",
    "auth_middleware",
    "apply_scope_filter",
    "get_scope_for_resource",
    "InterfaceType",
    "public_api",
    "login_required",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "verify_token",
    "parse_jwt_token",
    "get_password_hash",
    "verify_password",
    "generate_password",
    "pwd_context",
    "token_manager",
]
