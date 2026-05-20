"""
用户个人管理接口
"""

from fastapi import APIRouter, Request, Depends, HTTPException, Body
from pydantic import BaseModel

from src.models.sys.user import User
from src.schemas.sys.users import UpdatePassword, UserUpdate
from src.services.sys.user_service import user_service
from src.core.response import success
from src.core.dependency import AuthControl
from src.core.storage import token_manager
from src.core.rate_limit import apply_rate_limit
from src.core.log import logger


router = APIRouter()


class LogoutRequest(BaseModel):
    """登出请求"""
    refresh_token: str | None = None


@router.post("/change_password", summary="修改密码")
@apply_rate_limit("10/minute")
def change_password(
    request: Request,
    password_in: UpdatePassword,
    current_user: User = Depends(AuthControl.is_authed),
):
    result = user_service.change_user_password(
        user_id=current_user.id,
        old_password=password_in.old_password,
        new_password=password_in.new_password,
    )
    if not result:
        raise HTTPException(status_code=400, detail="旧密码错误")

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
        raise HTTPException(status_code=401, detail="认证失败")

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


@router.put("/profile", summary="更新个人信息")
@apply_rate_limit("30/minute")
def update_profile(
    request: Request,
    user_in: UserUpdate,
    current_user: User = Depends(AuthControl.is_authed),
):
    user_service.update_user(current_user.id, user_in)
    return success(msg="个人信息更新成功")


@router.get("/profile", summary="获取个人信息")
@apply_rate_limit("60/minute")
def get_profile(request: Request, current_user: User = Depends(AuthControl.is_authed)):
    user_dict = current_user.to_dict()
    return success(data=user_dict)
