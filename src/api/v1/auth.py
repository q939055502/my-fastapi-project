"""
认证接口（注册、登录、Token刷新）
"""

from fastapi import APIRouter, Request

from src.core.enums.response_code import ResponseCode
from src.core.exceptions.exception import BusinessException
from src.core.handlers import gen_swagger_response, success
from src.core.handlers.response import ApiResponse
from src.core.plugins import apply_rate_limit
from src.core.settings.router_config import DEFAULT_ROUTER_RESPONSES
from src.schemas.sys.login import (
    CredentialsSchema,
    JWTOut,
    RefreshTokenRequest,
    TokenRefreshOut,
    UserRegisterOut,
    UserRegisterSchema,
)
from src.services.sys.auth_service import auth_service

# APIRouter 级别配置：系统级错误响应（所有子接口自动继承）
router = APIRouter(
    tags=["认证"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/register",
    summary="用户注册",
    response_model=ApiResponse[UserRegisterOut],
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.DATA_ALREADY_EXIST],
            description="用户名或邮箱已存在"
        ),
    },
)
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
    if not result:
        raise BusinessException(ResponseCode.DATA_ALREADY_EXIST)
    return success(data=result, msg="注册成功")


@router.post(
    "/login",
    summary="用户登录",
    response_model=ApiResponse[JWTOut],
    responses={
        200: gen_swagger_response(
            codes=[ResponseCode.SUCCESS],
            description="登录成功",
            example_data={"access_token": "xxx", "refresh_token": "yyy", "token_type": "bearer"}
        ),
        401: gen_swagger_response(
            codes=[ResponseCode.UNAUTHORIZED, ResponseCode.TOKEN_EXPIRED, ResponseCode.TOKEN_FORMAT_INVALID],
            description="未授权/Token异常"
        ),
    },
)
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
    if not auth_data:
        raise BusinessException(ResponseCode.UNAUTHORIZED)
    data = JWTOut(**auth_data)
    return success(data=data.model_dump())


@router.post(
    "/refresh",
    summary="刷新token",
    response_model=ApiResponse[TokenRefreshOut],
    responses={
        401: gen_swagger_response(
            codes=[ResponseCode.UNAUTHORIZED, ResponseCode.TOKEN_EXPIRED, ResponseCode.TOKEN_FORMAT_INVALID],
            description="Token已过期或无效"
        ),
    },
)
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
    if not auth_data:
        raise BusinessException(ResponseCode.UNAUTHORIZED)
    data = TokenRefreshOut(**auth_data)
    return success(data=data.model_dump())
