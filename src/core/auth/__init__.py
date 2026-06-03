"""
认证模块

整合所有认证相关功能：
- security: 密码哈希、JWT生成/验证
- dependency: 认证控制、权限控制、依赖注入
- token: Redis令牌管理
- auth_context: 请求上下文管理
"""

from .auth_context import (
    AuthContext,
    get_auth_context,
    get_current_client_ip,
    get_current_member_id,
    get_current_request_id,
    get_current_tenant_id,
    get_current_user_id,
)

# 保留旧的 ContextVar 导出以保持向后兼容
from .context import (
    CTX_BG_TASKS,
    CTX_MEMBER_ID,
    CTX_REQUEST_ID,
    CTX_TENANT_ID,
    CTX_USER_ID,
    clear_context,
    set_current_member_id,
    set_current_tenant_id,
    set_current_user_id,
)
from .dependency import AuthControl, PermissionControl, get_current_username
from .security import (
    check_perm_match,
    create_access_token,
    create_refresh_token,
    create_token_pair,
    gen_perm_code,
    generate_password,
    get_password_hash,
    parse_jwt_token,
    pwd_context,
    verify_password,
    verify_token,
)
from .token import token_manager

__all__ = [
    # security
    "pwd_context",
    "get_password_hash",
    "verify_password",
    "generate_password",
    "create_access_token",
    "create_refresh_token",
    "create_token_pair",
    "verify_token",
    "parse_jwt_token",
    "gen_perm_code",
    "check_perm_match",
    # dependency
    "AuthControl",
    "PermissionControl",
    "get_current_username",
    # auth_context (新方案)
    "AuthContext",
    "get_auth_context",
    "get_current_user_id",
    "get_current_member_id",
    "get_current_tenant_id",
    "get_current_request_id",
    "get_current_client_ip",
    # context (旧方案，保持兼容)
    "CTX_USER_ID",
    "CTX_MEMBER_ID",
    "CTX_TENANT_ID",
    "CTX_BG_TASKS",
    "CTX_REQUEST_ID",
    "set_current_user_id",
    "set_current_member_id",
    "set_current_tenant_id",
    "clear_context",
    # token
    "token_manager",
]
