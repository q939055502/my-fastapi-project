"""
认证接口（注册、登录、Token刷新）
"""

from fastapi import APIRouter, Request
from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.plugins import apply_rate_limit
from src.common.core.response import ApiResponse, gen_swagger_response, success
from src.common.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.auth.schemas.login import (
    LoginByPasswordOut,
    LoginByPasswordStep1Request,
    LoginStep1MultiResponse,
)
from src.foundation.auth.schemas.register import (
    UserRegisterOut,
    UserRegisterSchema,
)
from src.foundation.auth.schemas.token import (
    RefreshTokenRequest,
    TokenRefreshOut,
)
from src.foundation.auth.schemas.user import (
    SelectUserOut,
    SelectUserRequest,
)
from src.foundation.auth.service.auth_service import auth_service

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
    "/login_by_account_and_password",
    summary="第一步登录",
    response_model=ApiResponse[LoginByPasswordOut] | ApiResponse[LoginStep1MultiResponse],

    responses={
        200: gen_swagger_response(
            codes=[ResponseCode.SUCCESS],
            description="登录成功（单账号返回正式令牌，多账号返回临时凭证）",
        ),
        401: gen_swagger_response(
            codes=[ResponseCode.UNAUTHORIZED],
            description="未授权"
        ),
    },
)
@apply_rate_limit()
def login_by_account_and_password(request: Request, credentials: LoginByPasswordStep1Request):
    """
    用户第一步登录接口（密码登录）

    【类型】公开接口（无需登录）
    【权限】无需认证
    【限流】5次/分钟（防暴力破解）
    【功能】验证用户名密码，单账号直接返回正式令牌，多账号返回临时凭证供选择
    """
    from src.common.core.context.auth_context import get_current_client_ip
    client_ip = get_current_client_ip(request)
    auth_data = auth_service.login_by_account_and_password(credentials, client_ip)
    if not auth_data:
        raise BusinessException(ResponseCode.UNAUTHORIZED)

    # 根据返回数据类型使用对应的响应模型
    if "access_token" in auth_data:
        data = LoginByPasswordOut(**auth_data)
        return success(data=data.model_dump(), msg="登录成功")
    else:
        data = LoginStep1MultiResponse(**auth_data)
        return success(data=data.model_dump(), msg="请选择用户")


@router.post(
    "/select-user",
    summary="第二步登录（选择用户）",
    response_model=ApiResponse[SelectUserOut],
    responses={
        200: gen_swagger_response(
            codes=[ResponseCode.SUCCESS],
            description="登录成功",
            example_data={
                "access_token": "xxx",
                "refresh_token": "yyy",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {"uuid": "550e8400-e29b-41d4-a716-446655440000", "username": "admin", "email": "admin@example.com"}
            }
        ),
        401: gen_swagger_response(
            codes=[ResponseCode.UNAUTHORIZED],
            description="无效的临时登录凭证"
        ),
        403: gen_swagger_response(
            codes=[ResponseCode.FORBIDDEN],
            description="用户不在可选择列表中或已被禁用"
        ),
    },
)
@apply_rate_limit()
def select_user(request: Request, select_request: SelectUserRequest):
    """
    用户第二步登录接口（选择用户）

    【类型】公开接口（无需登录）
    【权限】无需认证
    【限流】10次/分钟
    【功能】多账号场景下选择用户，返回正式业务令牌
    """
    from src.common.core.context.auth_context import get_current_client_ip
    client_ip = get_current_client_ip(request)
    auth_data = auth_service.select_user(select_request.temp_token, select_request.user_uuid, client_ip)
    if not auth_data:
        raise BusinessException(ResponseCode.UNAUTHORIZED)
    data = SelectUserOut(**auth_data)
    return success(data=data.model_dump(), msg="登录成功")


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
