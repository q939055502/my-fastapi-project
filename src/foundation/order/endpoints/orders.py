"""
订单管理接口
"""
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from src.core.enums.response_code import ResponseCode
from src.core.plugins import apply_rate_limit
from src.core.response import gen_swagger_response, success, success_page
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.iam import AuthControl, PermissionControl
from src.foundation.order.schemas.order import (
    OrderCancelRequest,
    OrderCreate,
    OrderUpdate,
)
from src.foundation.order.service import order_service

router = APIRouter(
    tags=["订单管理"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/",
    summary="创建订单",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.PARAM_ERROR],
            description="参数错误",
        ),
    },
)
@apply_rate_limit("30/minute")
def create_order(
    request: Request,
    order_in: OrderCreate,
    current_user = Depends(AuthControl.is_authed),
):
    """
    创建订单
    """
    order_data = order_service.create_order(
        order_in=order_in,
        operator_id=current_user.id,
        operator_name=current_user.username,
    )
    return success(data=order_data, msg="订单创建成功")


@router.get("/list", summary="获取订单列表")
@apply_rate_limit("60/minute")
def list_orders(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    buyer_type: str = Query(None, description="购买主体类型：tenant/user"),
    buyer_id: int = Query(None, description="购买主体ID"),
    product_type: str = Query(None, description="商品类型：member/service"),
    product_id: int = Query(None, description="商品ID"),
    order_type: str = Query(None, description="订单类型：new/renew/upgrade"),
    pay_status: str = Query(None, description="支付状态"),
    order_status: str = Query(None, description="订单状态"),
    order_no: str = Query(None, description="订单号"),
    start_time: datetime = Query(None, description="开始时间"),
    end_time: datetime = Query(None, description="结束时间"),
    current_user = Depends(AuthControl.is_authed),
):
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
    return success_page(data=data, total=total, page=page, page_size=page_size)


@router.get(
    "/{order_uuid}",
    summary="获取订单详情",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="订单不存在",
        ),
    },
)
@apply_rate_limit("60/minute")
def get_order_detail(
    request: Request,
    order_uuid: UUID,
    current_user = Depends(AuthControl.is_authed),
):
    """
    获取订单详情
    """
    order_data = order_service.get_order_detail(order_uuid)
    return success(data=order_data)


@router.put(
    "/{order_uuid}",
    summary="更新订单",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="订单不存在",
        ),
    },
)
@apply_rate_limit("30/minute")
def update_order(
    request: Request,
    order_uuid: UUID,
    order_in: OrderUpdate,
    current_user = Depends(AuthControl.is_authed),
):
    """
    更新订单
    """
    order_data = order_service.update_order(order_uuid, order_in)
    return success(data=order_data, msg="订单更新成功")


@router.post(
    "/{order_uuid}/cancel",
    summary="取消订单",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="订单不存在",
        ),
        400: gen_swagger_response(
            codes=[ResponseCode.PARAM_ERROR],
            description="已支付订单不能直接取消",
        ),
    },
)
@apply_rate_limit("30/minute")
def cancel_order(
    request: Request,
    order_uuid: UUID,
    cancel_in: OrderCancelRequest = None,
    current_user = Depends(AuthControl.is_authed),
):
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
    return success(msg="订单已取消")


@router.get(
    "/{order_uuid}/logs",
    summary="获取订单操作日志",
)
@apply_rate_limit("60/minute")
def get_order_logs(
    request: Request,
    order_uuid: UUID,
    current_user = Depends(AuthControl.is_authed),
):
    """
    获取订单操作日志
    """
    logs = order_service.list_order_logs(order_uuid)
    return success(data=logs)


# 管理员接口 - 需要权限
admin_router = APIRouter(
    tags=["订单管理-管理员"],
    responses=DEFAULT_ROUTER_RESPONSES,
    prefix="/admin",
    dependencies=[Depends(PermissionControl.has_permission)],
)


@admin_router.get("/orders", summary="管理员获取所有订单")
@apply_rate_limit("60/minute")
def admin_list_orders(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(20, description="每页数量"),
    buyer_type: str = Query(None, description="购买主体类型"),
    pay_status: str = Query(None, description="支付状态"),
    order_status: str = Query(None, description="订单状态"),
):
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
    return success_page(data=data, total=total, page=page, page_size=page_size)