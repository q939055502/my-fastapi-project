"""
Auth 认证 Schema

包含:登录, 注册, 刷新令牌等认证相关 Schema
"""

from .login import (
    LoginByPasswordStep1Request,
    LoginResponse,
    LoginSelectUserResponse,
)
from .register import (
    UserRegisterResponse,
    UserRegisterSchema,
)
from .tenant import (
    SelectTenantRequest,
    TenantInfoSchema,
)
from .token import (
    JWTPayload,
    RefreshTokenRequest,
    TokenRefreshResponse,
)
from .user import (
    SelectUserRequest,
    SelectUserResponse,
    UserInfoSchema,
)

__all__ = [
    "LoginResponse",
    "LoginByPasswordStep1Request",
    "LoginSelectUserResponse",
    "UserRegisterResponse",
    "UserRegisterSchema",
    "SelectTenantRequest",
    "TenantInfoSchema",
    "JWTPayload",
    "RefreshTokenRequest",
    "TokenRefreshResponse",
    "SelectUserResponse",
    "SelectUserRequest",
    "UserInfoSchema",
]
