"""
API v1 版本路由注册
"""
from fastapi import APIRouter

from src.foundation.auth.api.v1 import auth_v1_router
from src.foundation.system.api.v1 import common_v1_router
from src.foundation.platform.api.v1 import platform_v1_router
from src.foundation.tenant.api.v1 import tenant_v1_router
from src.modules.order.api.v1 import order_v1_router

v1_router = APIRouter()

v1_router.include_router(auth_v1_router)
v1_router.include_router(common_v1_router)
v1_router.include_router(platform_v1_router)
v1_router.include_router(tenant_v1_router, prefix="/{tenant_key}")
v1_router.include_router(order_v1_router)

__all__ = ["v1_router"]