"""
认证接口（注册、登录、Token刷新）
"""

from fastapi import APIRouter, Request

from src.core.handlers import success
from src.core.plugins import apply_rate_limit
from src.schemas.sys.login import (
    CredentialsSchema,
    JWTOut,
    RefreshTokenRequest,
    TokenRefreshOut,
    UserRegisterSchema,
)
from src.services.sys.auth_service import auth_service

router = APIRouter(tags=["认证"])


@router.post("/register", summary="用户注册")
@apply_rate_limit("10/minute")
def user_register(request: Request, register_in: UserRegisterSchema):
    """
    用户自主注册接口

    【类型】公开接口（无需登录）
    【权限】无需认证
    【限流】10次/分钟（防恶意注册）
    【功能】创建新用户账户，默认分配普通用户角色
    【自动登录】配置开启时，注册成功后自动返回登录Token
    """
    result = auth_service.register(register_in)
    return success(data=result, msg="注册成功")


@router.post("/login", summary="用户登录")
@apply_rate_limit()
def login_access_token(request: Request, credentials: CredentialsSchema):
    """
    用户登录接口

    【类型】公开接口（无需登录）
    【权限】无需认证
    【限流】5次/分钟（防暴力破解）
    【功能】验证用户名密码，返回 access_token 和 refresh_token
    """
    auth_data = auth_service.login(credentials)
    data = JWTOut(**auth_data)
    return success(data=data.model_dump())


@router.post("/refresh", summary="刷新token")
@apply_rate_limit("10/minute")
def refresh_access_token(request: Request, refresh_request: RefreshTokenRequest):
    """
    刷新访问令牌

    【类型】认证接口
    【权限】使用 refresh_token 换发新token（无需 access_token）
    【限流】10次/分钟
    【功能】用 refresh_token 获取新的 access_token 和 refresh_token
    """
    auth_data = auth_service.refresh_token(refresh_request)
    data = TokenRefreshOut(**auth_data)
    return success(data=data.model_dump())
