"""
订单管理接口
"""
from datetime import datetime
from typing import Annotated, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse, swagger_responses
from src.foundation.iam import AuthControl, require_permission
from src.foundation.order.schemas.order import (
    OrderCancelRequest,
    OrderCreate,
    OrderListResponse,
    OrderResponse,
    OrderUpdate,
)
from src.foundation.order.service import order_service

T = TypeVar("T")

router = APIRouter(
    tags=["订单管理"],
)


class OrderListDataResponse(BaseModel):
    """订单分页列表响应数据"""

    list: Annotated[list[OrderListResponse], Field(description="订单列表")]
    total: int = Field(description="总记录数")
    page: int = Field(description="当前页码")
    page_size: int = Field(description="每页数量")
    total_pages: int = Field(description="总页数")


@router.post(
    "/",
    summary="创建订单",
)
@apply_rate_limit("30/minute")
def create_order(
    request: Request,
    order_in: OrderCreate,
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[OrderResponse]:
    """
    创建订单
    """
    order_data = order_service.create_order(
        order_in=order_in,
        operator_id=current_user.id,
        operator_name=current_user.username,
    )
    return ApiResponse(
        code=20000,
        msg="订单创建成功",
        data=OrderResponse.model_validate(order_data),
    )


@router.get("/list", summary="获取订单列表")
@apply_rate_limit("60/minute")
def list_orders(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    buyer_type: str = Query(None, description="购买主体类型:tenant/user"),
    buyer_id: int = Query(None, description="购买主体ID"),
    product_type: str = Query(None, description="商品类型:member/service"),
    product_id: int = Query(None, description="商品ID"),
    order_type: str = Query(None, description="订单类型:new/renew/upgrade"),
    pay_status: str = Query(None, description="支付状态"),
    order_status: str = Query(None, description="订单状态"),
    order_no: str = Query(None, description="订单编号"),
    start_time: datetime = Query(None, description="开始时间"),
    end_time: datetime = Query(None, description="结束时间"),
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[OrderListDataResponse]:
    """
    获取订单列表
    """
    total, data = order_service.list_orders(
        page=page,
        page_size=page_size,
        buyer_type=buyer_type,
        buyer_id=buyer_id,
        product_type=product_type,
        product_id=product_id,
        order_type=order_type,
        pay_status=pay_status,
        order_status=order_status,
        order_no=order_no,
        start_time=start_time,
        end_time=end_time,
    )
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ApiResponse(
        code=20000,
        msg="操作成功",
        data=OrderListDataResponse(
            list=[OrderListResponse.model_validate(order) for order in data],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )


@router.get(
    "/{order_uuid}",
    summary="获取订单详情",
    responses=swagger_responses(
        codes=[40401],
        success_msg="订单不存在",
    ),
)
@apply_rate_limit("60/minute")
def get_order_detail(
    request: Request,
    order_uuid: UUID,
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[OrderResponse]:
    """
    获取订单详情
    """
    order_data = order_service.get_order_detail(order_uuid)
    return ApiResponse(
        code=20000,
        msg="操作成功",
        data=OrderResponse.model_validate(order_data),
    )


@router.put(
    "/{order_uuid}",
    summary="更新订单",
)
@apply_rate_limit("30/minute")
def update_order(
    request: Request,
    order_uuid: UUID,
    order_in: OrderUpdate,
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[OrderResponse]:
    """
    更新订单
    """
    order_data = order_service.update_order(order_uuid, order_in)
    return ApiResponse(
        code=20000,
        msg="订单更新成功",
        data=OrderResponse.model_validate(order_data),
    )


@router.post(
    "/{order_uuid}/cancel",
    summary="取消订单",
    responses=swagger_responses(
        codes=[40401, 40000],
        success_msg="订单不存在",
    ),
)
@apply_rate_limit("30/minute")
def cancel_order(
    request: Request,
    order_uuid: UUID,
    cancel_in: OrderCancelRequest = None,
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[None]:
    """
    取消订单
    """
    reason = cancel_in.reason if cancel_in else None
    order_service.cancel_order(
        order_uuid,
        reason=reason,
        operator_id=current_user.id,
        operator_name=current_user.username,
    )
    return ApiResponse(
        code=20000,
        msg="订单已取消",
        data=None,
    )


@router.get(
    "/{order_uuid}/logs",
    summary="获取订单操作日志",
)
@apply_rate_limit("60/minute")
def get_order_logs(
    request: Request,
    order_uuid: UUID,
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[None]:
    """
    获取订单操作日志
    """
    logs = order_service.list_order_logs(order_uuid)
    return ApiResponse(
        code=20000,
        msg="操作成功",
        data=logs,
    )


# 管理员接口 - 需要权限
admin_router = APIRouter(
    tags=["订单管理-管理员"],
    prefix="/admin",
)


@admin_router.get("/orders", summary="管理员获取所有订单", dependencies=[require_permission("platform:order:list")])
@apply_rate_limit("60/minute")
def admin_list_orders(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    buyer_type: str = Query(None, description="购买主体类型"),
    pay_status: str = Query(None, description="支付状态"),
    order_status: str = Query(None, description="订单状态"),
) -> ApiResponse[OrderListDataResponse]:
    """
    管理员获取所有订单
    """
    total, data = order_service.list_orders(
        page=page,
        page_size=page_size,
        buyer_type=buyer_type,
        pay_status=pay_status,
        order_status=order_status,
    )
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ApiResponse(
        code=20000,
        msg="操作成功",
        data=OrderListDataResponse(
            list=[OrderListResponse.model_validate(order) for order in data],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        ),
    )
