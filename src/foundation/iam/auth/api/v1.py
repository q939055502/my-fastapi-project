"""
认证模块 API v1 版本路由
"""

from fastapi import APIRouter, Depends, Request

from src.foundation.iam.auth.endpoints.auth import (
    login_by_account_and_password,
    select_user,
    user_register,
    refresh_access_token,
)
from src.core.annotations import public_api, login_required

auth_v1_router = APIRouter(prefix="/auth", tags=["认证"])

auth_v1_router.post("/login")(public_api(login_by_account_and_password))
auth_v1_router.post("/select_user")(public_api(select_user))
auth_v1_router.post("/register")(public_api(user_register))
auth_v1_router.post("/refresh")(public_api(refresh_access_token))

# TODO: 以下路由预留，暂未实现
# auth_v1_router.post("/send_captcha")(public_api(send_captcha))
# auth_v1_router.post("/login_captcha")(public_api(login_by_captcha))

__all__ = ["auth_v1_router"]
