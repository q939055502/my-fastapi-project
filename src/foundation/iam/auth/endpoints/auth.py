"""
认证接口(注册, 登录, Token刷新)
"""

from fastapi import APIRouter, Request

from src.core.exceptions import BusinessException
from src.core.plugins import apply_rate_limit
from src.core.annotations import InterfaceType, interface_type
from src.core.response import ApiResponse, success, swagger_responses
from src.foundation.iam.auth.schemas.login import (
    LoginByPasswordStep1Request,
    LoginResponse,
    LoginSelectUserResponse,
)
from src.foundation.iam.auth.schemas.register import (
    UserRegisterResponse,
    UserRegisterSchema,
)
from src.foundation.iam.auth.schemas.token import (
    RefreshTokenRequest,
    TokenRefreshResponse,
)
from src.foundation.iam.auth.schemas.user import (
    SelectUserRequest,
    SelectUserResponse,
)
from src.foundation.iam.auth.service.auth_service import auth_service

router = APIRouter(
    tags=["认证"],
)


@router.post(
    "/register",
    summary="用户注册",
    response_model=ApiResponse[UserRegisterResponse],
    responses=swagger_responses(
        codes=[20000, 40900],
        data_model=UserRegisterResponse,
        success_msg="注册成功",
        interface_type=InterfaceType.PUBLIC,
    ),
)
@apply_rate_limit("10/minute")
@interface_type(InterfaceType.PUBLIC)
def user_register(request: Request, register_in: UserRegisterSchema):
    result = auth_service.register(register_in)
    if not result:
        raise BusinessException(40900)
    return success(data=result, msg="注册成功")


@router.post(
    "/login_by_account_and_password",
    summary="第一步登录",
    response_model=ApiResponse[LoginResponse] | ApiResponse[LoginSelectUserResponse],
    responses=swagger_responses(
        codes=[20000, 20007],
        code_model_map={
            20000: LoginResponse,
            20007: LoginSelectUserResponse,
        },
        success_msg="登录成功(单账号返回正式令牌,多账号返回临时凭证)",
        interface_type=InterfaceType.PUBLIC,
    ),
)
@apply_rate_limit()
@interface_type(InterfaceType.PUBLIC)
def login_by_account_and_password(request: Request, credentials: LoginByPasswordStep1Request):
    from src.foundation.iam.auth.context import get_current_client_ip
    client_ip = get_current_client_ip(request)
    auth_data = auth_service.login_by_account_and_password(credentials, client_ip)
    if not auth_data:
        raise BusinessException(40100)

    if "access_token" in auth_data:
        data = LoginResponse(**auth_data)
        return success(data=data.model_dump(), msg="登录成功")
    else:
        data = LoginSelectUserResponse(**auth_data)
        return success(data=data.model_dump(), msg="请选择用户")


@router.post(
    "/select-user",
    summary="第二步登录(选择用户)",
    response_model=ApiResponse[SelectUserResponse],
    responses=swagger_responses(
        codes=[20000],
        data_model=SelectUserResponse,
        success_msg="登录成功",
        interface_type=InterfaceType.PUBLIC,
    ),
)
@apply_rate_limit()
@interface_type(InterfaceType.PUBLIC)
def select_user(request: Request, select_request: SelectUserRequest):
    from src.foundation.iam.auth.context import get_current_client_ip
    client_ip = get_current_client_ip(request)
    auth_data = auth_service.select_user(select_request.temp_token, str(select_request.user_uuid), client_ip)
    if not auth_data:
        raise BusinessException(40100)
    data = SelectUserResponse(**auth_data)
    return success(data=data.model_dump(), msg="登录成功")


@router.post(
    "/refresh",
    summary="刷新token",
    response_model=ApiResponse[TokenRefreshResponse],
    responses=swagger_responses(
        codes=[20000],
        data_model=TokenRefreshResponse,
        success_msg="刷新成功",
        interface_type=InterfaceType.PUBLIC,
    ),
)
@apply_rate_limit("10/minute")
@interface_type(InterfaceType.PUBLIC)
def refresh_access_token(request: Request, refresh_request: RefreshTokenRequest):
    auth_data = auth_service.refresh_token(refresh_request)
    if not auth_data:
        raise BusinessException(40100)
    data = TokenRefreshResponse(**auth_data)
    return success(data=data.model_dump())


# TODO: 以下接口预留,暂未实现
