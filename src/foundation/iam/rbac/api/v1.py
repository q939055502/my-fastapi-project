"""
RBAC 模块 API v1 版本路由
"""

from fastapi import APIRouter

from src.core.annotations import interface_type, InterfaceType

rbac_v1_router = APIRouter(prefix="/rbac", tags=["权限管理"])

__all__ = ["rbac_v1_router"]
