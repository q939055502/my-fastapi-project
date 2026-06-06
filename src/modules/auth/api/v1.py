"""
认证模块 API v1 路由
"""
from fastapi import APIRouter

from ..endpoints.auth import router as auth_router

auth_v1_router = APIRouter()

auth_v1_router.include_router(auth_router, prefix="/auth")

__all__ = ["auth_v1_router"]
