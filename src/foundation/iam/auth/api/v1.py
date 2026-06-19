"""
认证模块 API v1 版本路由
"""

from fastapi import APIRouter

from src.foundation.iam.auth.endpoints.auth import router as auth_router

auth_v1_router = APIRouter(prefix="/auth", tags=["认证"])

auth_v1_router.include_router(auth_router)


__all__ = ["auth_v1_router"]
