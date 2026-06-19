"""
订单模块 API v1 路由
"""
from fastapi import APIRouter

from ..endpoints.payments import router as payments_router

order_v1_router = APIRouter()
order_v1_router.include_router(payments_router, prefix="/orders")

__all__ = ["order_v1_router"]
