"""
订单支付与退款接口
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from src.core.enums.response_code import ResponseCode
from src.core.plugins import apply_rate_limit
from src.core.response import gen_swagger_response, success
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.iam import AuthControl
from src.foundation.order.schemas.order_payment import OrderPaymentCreate
from src.foundation.order.schemas.order_refund import OrderRefundCreate
from src.foundation.order.service import (
    order_payment_service,
    order_refund_service,
)

router = APIRouter(
    tags=["订单管理-支付退款"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/{order_uuid}/payments",
    summary="创建支付记录",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="订单不存在",
        ),
    },
)
@apply_rate_limit("30/minute")
def create_payment(
    request: Request,
    order_uuid: UUID,
    payment_in: OrderPaymentCreate,
    current_user = Depends(AuthControl.is_authed),
):
    """
    创建支付记录（标记订单为已支付）
    """
    payment_data = order_payment_service.create_payment(
        order_uuid,
        payment_in,
        operator_id=current_user.id,
        operator_name=current_user.username,
    )
    return success(data=payment_data, msg="支付成功")


@router.get(
    "/{order_uuid}/payments",
    summary="获取订单支付记录",
)
@apply_rate_limit("60/minute")
def list_payments(
    request: Request,
    order_uuid: UUID,
    current_user = Depends(AuthControl.is_authed),
):
    """
    获取订单支付记录
    """
    payments = order_payment_service.list_payments(order_uuid)
    return success(data=payments)


@router.post(
    "/{order_uuid}/refunds",
    summary="申请退款",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.ENTITY_NOT_FOUND],
            description="订单不存在",
        ),
        400: gen_swagger_response(
            codes=[ResponseCode.PARAM_ERROR],
            description="只有已支付订单可申请退款",
        ),
    },
)
@apply_rate_limit("10/minute")
def create_refund(
    request: Request,
    order_uuid: UUID,
    refund_in: OrderRefundCreate,
    current_user = Depends(AuthControl.is_authed),
):
    """
    申请退款
    """
    refund_data = order_refund_service.create_refund(
        order_uuid,
        refund_in,
        operator_id=current_user.id,
        operator_name=current_user.username,
    )
    return success(data=refund_data, msg="退款申请已提交")


@router.get(
    "/{order_uuid}/refunds",
    summary="获取订单退款记录",
)
@apply_rate_limit("60/minute")
def list_refunds(
    request: Request,
    order_uuid: UUID,
    current_user = Depends(AuthControl.is_authed),
):
    """
    获取订单退款记录
    """
    refunds = order_refund_service.list_refunds(order_uuid)
    return success(data=refunds)