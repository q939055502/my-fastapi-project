"""
订单模块 API v1 路由
"""
from fastapi import APIRouter

from ..endpoints.payments import router as payments_router

order_v1_router = APIRouter()

# 用户端订单接�?order_v1_router.include_router(orders_router, prefix="/orders")
order_v1_router.include_router(payments_router, prefix="/orders")

# 管理员订单接�?order_v1_router.include_router(admin_orders_router)

__all__ = ["order_v1_router"]
