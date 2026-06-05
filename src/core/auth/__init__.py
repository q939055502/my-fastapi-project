"""
认证模块

整合所有认证相关功能：
- security: 密码哈希、JWT生成/验证
- dependency: 认证控制、权限控制、依赖注入
- token: Redis令牌管理
"""

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
    # token
    "token_manager",
]
