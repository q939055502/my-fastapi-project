"""
用户个人管理接口
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from src.core.exceptions import BusinessException
from src.core.log import logger
from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse, swagger_responses
from src.foundation.iam import AuthControl, token_manager
from src.foundation.system.schemas.user import (
    UpdateMyProfileIn,
    UpdatePassword,
    UserProfileResponse,
)
from src.foundation.system.service.user_service import user_service
from src.models.platform import User

router = APIRouter(
    tags=["个人中心"],
)


class LogoutRequest(BaseModel):
    """登出请求"""
    refresh_token: str | None = None


class SwitchTenantRequest(BaseModel):
    """切换租户请求"""
    tenant_uuid: UUID = Field(..., description="要切换的租户UUID")


@router.post(
    "/switch_tenant",
    summary="切换租户",
    response_model=ApiResponse,
    responses=swagger_responses(
        codes=[20000, 40300],
        success_msg="切换成功",
    ),
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
    【功能】切换到指定的租户,返回新的令牌
    """
    result = user_service.switch_tenant(current_user.uuid, switch_req.tenant_uuid)
    return ApiResponse(code=20000, data=result, msg="切换租户成功")


@router.post(
    "/change_password",
    summary="修改密码",
)
@apply_rate_limit("10/minute")
def change_password(
    request: Request,
    password_in: UpdatePassword,
    current_user: User = Depends(AuthControl.is_authed),
):
    result = user_service.change_my_password(
        user_uuid=current_user.uuid,
        old_password=password_in.old_password,
        new_password=password_in.new_password,
    )
    if not result:
        raise BusinessException(40000, detail="旧密码错误")

    token_manager.revoke_user_all_tokens(current_user.id)
    logger.info(f"密码修改成功,已强制所有设备下线 - user_id={current_user.id}")

    return ApiResponse(code=20000, msg="密码修改成功,所有设备已强制下线")


@router.post("/logout", summary="登出")
@apply_rate_limit("30/minute")
def logout(
    request: Request,
    logout_req: LogoutRequest,
    current_user: User = Depends(AuthControl.is_authed),
):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise BusinessException(40100, detail="认证失败")

    access_token = auth_header[len("Bearer "):]

    token_manager.revoke_access_token(access_token)

    if logout_req.refresh_token:
        token_manager.revoke_refresh_token(logout_req.refresh_token)
        token_manager.remove_token_from_user_set(current_user.id, access_token, logout_req.refresh_token)
        logger.info(f"登出成功,refresh_token已撤销 - user_id={current_user.id}")
    else:
        logger.warning(f"登出成功,但未提供refresh_token,refresh_token仍然有效 - user_id={current_user.id}")

    return ApiResponse(code=20000, msg="登出成功")


@router.post("/logout_all", summary="所有设备下线")
@apply_rate_limit("10/minute")
def logout_all(request: Request, current_user: User = Depends(AuthControl.is_authed)):
    count = token_manager.revoke_user_all_tokens(current_user.id)
    return ApiResponse(code=20000, msg=f"已撤销 {count} 个令牌")


@router.put(
    "/profile",
    summary="更新个人信息",
    response_model=ApiResponse[UserProfileResponse],
    responses=swagger_responses(
        codes=[20000],
        data_model=UserProfileResponse,
        success_msg="更新成功",
    ),
)
@apply_rate_limit("30/minute")
def update_profile(
    request: Request,
    user_in: UpdateMyProfileIn,
    current_user: User = Depends(AuthControl.is_authed),
) -> ApiResponse[UserProfileResponse]:
    """
    更新当前登录用户的个人信息
    【类型】个人中心接口
    【权限】已登录
    【限流】30次/分钟
    【功能】允许修改 alias, avatar, gender, remark
    """
    update_data = user_in.model_dump(exclude_unset=True, exclude_none=True)
    result = user_service.update_my_profile(current_user.uuid, update_data)
    return ApiResponse(data=UserProfileResponse.model_validate(result), msg="个人信息更新成功")


@router.get(
    "/profile",
    summary="获取个人信息",
    response_model=ApiResponse[UserProfileResponse],
)
@apply_rate_limit("60/minute")
def get_profile(request: Request, current_user: User = Depends(AuthControl.is_authed)) -> ApiResponse[UserProfileResponse]:
    """
    获取当前登录用户的个人信息
    【类型】个人中心接口
    【权限】已登录
    【限流】60次/分钟
    【功能】返回当前用户的完整信息
    """
    user_profile = user_service.get_my_profile(current_user.uuid)
    return ApiResponse(data=UserProfileResponse.model_validate(user_profile), msg="获取成功")
