"""
认证模块

整合所有认证相关功能:
- security: 密码哈希, JWT生成/验证
- token: Redis令牌管理
- context: 认证上下文管理
- auth_control: 认证控制, 依赖注入
- annotations: 接口类型注解
"""

from src.core.annotations import (
    InterfaceType,
    disable_data_permission,
    interface_type,
    login_required,
)

from .auth_control import AuthControl, get_current_username
from .context import (
    AuthContext,
    get_auth_context,
    get_current_auth_context,
    get_current_client_ip,
    get_current_member_id,
    get_current_path_tenant_id,
    get_current_tenant_id,
    get_current_user_id,
    set_auth_context,
)
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
    # auth_control
    "AuthControl",
    "get_current_username",
    # token
    "token_manager",
    # annotations
    "InterfaceType",
    "interface_type",
    "login_required",
    "disable_data_permission",
    # context
    "AuthContext",
    "get_auth_context",
    "get_current_auth_context",
    "set_auth_context",
    "get_current_user_id",
    "get_current_member_id",
    "get_current_tenant_id",
    "get_current_path_tenant_id",
    "get_current_client_ip",
]
