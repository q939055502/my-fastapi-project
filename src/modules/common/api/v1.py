"""
公共模块 API v1 路由
"""
from fastapi import APIRouter, Depends
from src.common.core.auth import AuthControl

from ..endpoints.account_bind import router as account_bind_router
from ..endpoints.files import router as common_files_router
from ..endpoints.info import router as public_info_router
from ..endpoints.me import router as me_router

common_v1_router = APIRouter()

common_v1_router.include_router(public_info_router, prefix="/public")
common_v1_router.include_router(me_router, prefix="/me", dependencies=[Depends(AuthControl.is_authed)])
common_v1_router.include_router(account_bind_router, prefix="/account-binds", dependencies=[Depends(AuthControl.is_authed)])
common_v1_router.include_router(common_files_router, prefix="/common/files", dependencies=[Depends(AuthControl.is_authed)])

__all__ = ["common_v1_router"]
