"""
用户个人管理接口
"""

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from src.common.core.auth import AuthControl, token_manager
from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.log import logger
from src.common.core.plugins import apply_rate_limit
from src.common.core.response import ApiResponse, gen_swagger_response, success
from src.common.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.models.platform import User
from src.modules.common.schemas.user import UpdateMyProfileIn, UserProfileOut
from src.modules.platform.schemas.user import UpdatePassword
from src.modules.platform.service.user_service import user_service

router = APIRouter(
    tags=["个人中心"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


class LogoutRequest(BaseModel):
    """登出请求"""
    refresh_token: str | None = None


class SwitchTenantRequest(BaseModel):
    """切换租户请求"""
    tenant_id: int = Field(..., description="要切换的租户ID")





@router.post(
    "/switch_tenant",
    summary="切换租户",
    response_model=ApiResponse,
    responses={
        200: gen_swagger_response(
            codes=[ResponseCode.SUCCESS],
            description="切换成功",
            example_data={
                "access_token": "xxx",
                "refresh_token": "yyy",
                "token_type": "bearer",
                "expires_in": 3600
            }
        ),
        403: gen_swagger_response(
            codes=[ResponseCode.FORBIDDEN],
            description="您不属于该租户"
        ),
    },
)
@apply_rate_limit("10/minute")
def switch_tenant(
    request: Request,
    switch_req: SwitchTenantRequest,
    current_user: User = Depends(AuthControl.is_authed),
):
    """
    已登录用户切换租户

    【类型】个人中心接口
    【权限】已登录
    【限流】10次/分钟
    【功能】切换到指定的租户，返回新的令牌
    """
    result = user_service.switch_tenant(current_user.id, switch_req.tenant_id)
    return success(data=result, msg="切换租户成功")


@router.post(
    "/change_password",
    summary="修改密码",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.PARAM_ERROR],
            description="旧密码错误"
        ),
    },
)
@apply_rate_limit("10/minute")
def change_password(
    request: Request,
    password_in: UpdatePassword,
    current_user: User = Depends(AuthControl.is_authed),
):
    result = user_service.change_my_password(
        user_id=current_user.id,
        old_password=password_in.old_password,
        new_password=password_in.new_password,
    )
    if not result:
        raise BusinessException(ResponseCode.PARAM_ERROR, detail="旧密码错误")

    token_manager.revoke_user_all_tokens(current_user.id)
    logger.info(f"密码修改成功，已强制所有设备下线 - user_id={current_user.id}")

    return success(msg="密码修改成功，所有设备已强制下线")


@router.post("/logout", summary="登出")
@apply_rate_limit("30/minute")
def logout(
    request: Request,
    logout_req: LogoutRequest,
    current_user: User = Depends(AuthControl.is_authed),
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise BusinessException(ResponseCode.UNAUTHORIZED, detail="认证失败")

    access_token = auth_header[len("Bearer "):]

    token_manager.revoke_access_token(access_token)

    if logout_req.refresh_token:
        token_manager.revoke_refresh_token(logout_req.refresh_token)
        token_manager.remove_token_from_user_set(current_user.id, access_token, logout_req.refresh_token)
        logger.info(f"登出成功，refresh_token已撤销 - user_id={current_user.id}")
    else:
        logger.warning(f"登出成功，但未提供refresh_token，refresh_token仍然有效 - user_id={current_user.id}")

    return success(msg="登出成功")


@router.post("/logout_all", summary="所有设备下线")
@apply_rate_limit("10/minute")
def logout_all(request: Request, current_user: User = Depends(AuthControl.is_authed)):
    count = token_manager.revoke_user_all_tokens(current_user.id)
    return success(msg=f"已撤销 {count} 个令牌")


@router.put(
    "/profile",
    summary="更新个人信息",
    response_model=ApiResponse[UserProfileOut],
    responses={
        200: gen_swagger_response(
            codes=[ResponseCode.SUCCESS],
            description="更新成功",
            example_data={
                "id": 1,
                "username": "superadmin",
                "alias": None,
                "avatar": None,
                "gender": 0,
                "last_login": "2026-06-07T10:00:00",
                "last_login_ip": "127.0.0.1",
                "email": "admin@example.com",
                "phone": "13800138000",
                "remark": None
            }
        ),
    },
)
@apply_rate_limit("30/minute")
def update_profile(
    request: Request,
    user_in: UpdateMyProfileIn,
    current_user: User = Depends(AuthControl.is_authed),
):
    """
    更新当前登录用户的个人信息

    【类型】个人中心接口
    【权限】已登录
    【限流】30次/分钟
    【功能】允许修改 alias、avatar、gender、remark
    """
    # 个人信息只能修改特定字段
    update_data = user_in.model_dump(exclude_unset=True, exclude_none=True)
    result = user_service.update_my_profile(current_user.id, update_data)
    return success(data=result, msg="个人信息更新成功")


@router.get(
    "/profile",
    summary="获取个人信息",
    response_model=ApiResponse[UserProfileOut],
    responses={
        200: gen_swagger_response(
            codes=[ResponseCode.SUCCESS],
            description="获取成功",
            example_data={
                "id": 1,
                "username": "superadmin",
                "alias": None,
                "avatar": None,
                "gender": 0,
                "last_login": "2026-06-07T10:00:00",
                "last_login_ip": "127.0.0.1",
                "email": "admin@example.com",
                "phone": "13800138000",
                "remark": None
            }
        ),
    },
)
@apply_rate_limit("60/minute")
def get_profile(request: Request, current_user: User = Depends(AuthControl.is_authed)):
    """
    获取当前登录用户的个人信息

    【类型】个人中心接口
    【权限】已登录
    【限流】60次/分钟
    【功能】返回当前用户的完整信息
    """
    user_profile = user_service.get_my_profile(current_user.id)
    return success(data=user_profile)
