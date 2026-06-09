"""
认证模块

整合所有认证相关功能：
- security: 密码哈希、JWT生成/验证
- dependency: 认证控制、权限控制、依赖注入
- token: Redis令牌管理
- annotations: 接口类型注解
"""

from .annotations import (
    InterfaceType,
    disable_data_permission,
    interface_type,
    login_required,
    public_api,
)
from .dependency import AuthControl, get_current_username
from .permission import PermissionControl
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
    # token
    "token_manager",
    # annotations
    "InterfaceType",
    "interface_type",
    "public_api",
    "login_required",
    "disable_data_permission",
]
