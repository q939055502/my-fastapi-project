"""
Auth 认证 Schema

包含:登录, 注册, 刷新令牌等认证相关 Schema
"""

from .login import (
    LoginByPasswordOut,
    LoginByPasswordStep1Request,
    LoginStep1MultiResponse,
)
from .register import (
    UserRegisterOut,
    UserRegisterSchema,
)
from .tenant import (
    SelectTenantRequest,
    TenantInfoSchema,
)
from .token import (
    JWTOut,
    JWTPayload,
    RefreshTokenRequest,
    TokenRefreshOut,
)
from .user import (
    SelectUserOut,
    SelectUserRequest,
    UserInfoSchema,
)

__all__ = [
    "LoginByPasswordOut",
    "LoginByPasswordStep1Request",
    "LoginStep1MultiResponse",
    "UserRegisterOut",
    "UserRegisterSchema",
    "SelectTenantRequest",
    "TenantInfoSchema",
    "JWTOut",
    "JWTPayload",
    "RefreshTokenRequest",
    "TokenRefreshOut",
    "SelectUserOut",
    "SelectUserRequest",
    "UserInfoSchema",
]
