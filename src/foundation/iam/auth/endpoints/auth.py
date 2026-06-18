"""
认证接口（注册、登录、Token刷新）
"""

from fastapi import APIRouter, Request
from src.core.enums.response_code import ResponseCode
from src.core.exceptions import BusinessException
from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse, gen_swagger_response, success
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.iam.auth.schemas.login import (
    LoginByPasswordOut,
    LoginByPasswordStep1Request,
    LoginStep1MultiResponse,
)
from src.foundation.iam.auth.schemas.register import (
    UserRegisterOut,
    UserRegisterSchema,
)
from src.foundation.iam.auth.schemas.token import (
    RefreshTokenRequest,
    TokenRefreshOut,
)
from src.foundation.iam.auth.schemas.user import (
    SelectUserOut,
    SelectUserRequest,
)
from src.foundation.iam.auth.service.auth_service import auth_service

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
    from src.foundation.iam.auth.context import get_current_client_ip
    client_ip = get_current_client_ip(request)
    auth_data = auth_service.login_by_account_and_password(credentials, client_ip)
    if not auth_data:
        raise BusinessException(ResponseCode.UNAUTHORIZED)

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
                "user": {
                    "uuid": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "admin",
                    "email": "admin@example.com",
                    "phone": "13800138000",
                    "alias": "管理员",
                    "avatar": None,
                    "gender": 1,
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00",
                    "last_login": "2024-06-15T10:30:00",
                    "last_login_ip": "192.168.1.100"
                }
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
    from src.foundation.iam.auth.context import get_current_client_ip
    client_ip = get_current_client_ip(request)
    auth_data = auth_service.select_user(select_request.temp_token, str(select_request.user_uuid), client_ip)
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
    auth_data = auth_service.refresh_token(refresh_request)
    if not auth_data:
        raise BusinessException(ResponseCode.UNAUTHORIZED)
    data = TokenRefreshOut(**auth_data)
    return success(data=data.model_dump())


# TODO: 以下接口预留，暂未实现
# @router.post(
#     "/send_captcha",
#     summary="发送验证码",
#     responses={
#         200: gen_swagger_response(
#             codes=[ResponseCode.SUCCESS],
#             description="发送成功"
#         ),
#         400: gen_swagger_response(
#             codes=[ResponseCode.BAD_REQUEST],
#             description="参数错误"
#         ),
#     },
# )
# @apply_rate_limit("5/minute")
# def send_captcha(request: Request):
#     raise BusinessException(ResponseCode.NOT_IMPLEMENTED)


# @router.post(
#     "/login_by_captcha",
#     summary="验证码登录",
#     responses={
#         200: gen_swagger_response(
#             codes=[ResponseCode.SUCCESS],
#             description="登录成功"
#         ),
#         401: gen_swagger_response(
#             codes=[ResponseCode.UNAUTHORIZED],
#             description="验证码错误或已过期"
#         ),
#     },
# )
# @apply_rate_limit()
# def login_by_captcha(request: Request):
#     raise BusinessException(ResponseCode.NOT_IMPLEMENTED)
