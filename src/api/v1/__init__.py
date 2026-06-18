"""
API v1 版本路由注册
"""
from fastapi import APIRouter

from src.foundation.iam.auth.api.v1 import auth_v1_router
from src.foundation.system.api.v1 import system_v1_router
from src.foundation.iam.rbac.api.v1 import rbac_v1_router
from src.foundation.tenant.api.v1 import tenant_v1_router
from src.foundation.order.api.v1 import order_v1_router

v1_router = APIRouter()

v1_router.include_router(auth_v1_router)
v1_router.include_router(system_v1_router)
v1_router.include_router(rbac_v1_router)
v1_router.include_router(tenant_v1_router, prefix="/{tenant_key}")
v1_router.include_router(order_v1_router)

__all__ = ["v1_router"]