"""
订单支付与退款接口
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse, swagger_responses
from src.foundation.iam import AuthControl
from src.foundation.order.schemas.order_payment import (
    OrderPaymentCreate,
    OrderPaymentResponse,
)
from src.foundation.order.schemas.order_refund import (
    OrderRefundCreate,
    OrderRefundResponse,
)
from src.foundation.order.service import (
    order_payment_service,
    order_refund_service,
)

router = APIRouter(
    tags=["订单管理-支付退款"],
)


@router.post(
    "/{order_uuid}/payments",
    summary="创建支付记录",
    responses=swagger_responses(
        codes=[40401],
        success_msg="订单不存在",
    ),
)
@apply_rate_limit("30/minute")
def create_payment(
    request: Request,
    order_uuid: UUID,
    payment_in: OrderPaymentCreate,
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[OrderPaymentResponse]:
    """
    创建支付记录(标记订单为已支付)
    """
    payment_data = order_payment_service.create_payment(
        order_uuid,
        payment_in,
        operator_id=current_user.id,
        operator_name=current_user.username,
    )
    payment_response = OrderPaymentResponse.model_validate(payment_data)
    return ApiResponse(code=20000, data=payment_response, msg="支付成功")


@router.get(
    "/{order_uuid}/payments",
    summary="获取订单支付记录",
)
@apply_rate_limit("60/minute")
def list_payments(
    request: Request,
    order_uuid: UUID,
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[list[OrderPaymentResponse]]:
    """
    获取订单支付记录
    """
    payments = order_payment_service.list_payments(order_uuid)
    payment_responses = [OrderPaymentResponse.model_validate(p) for p in payments]
    return ApiResponse(code=20000, data=payment_responses)


@router.post(
    "/{order_uuid}/refunds",
    summary="申请退款",
)
@apply_rate_limit("10/minute")
def create_refund(
    request: Request,
    order_uuid: UUID,
    refund_in: OrderRefundCreate,
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[OrderRefundResponse]:
    """
    申请退款
    """
    refund_data = order_refund_service.create_refund(
        order_uuid,
        refund_in,
        operator_id=current_user.id,
        operator_name=current_user.username,
    )
    refund_response = OrderRefundResponse.model_validate(refund_data)
    return ApiResponse(code=20000, data=refund_response, msg="退款申请已提交")


@router.get(
    "/{order_uuid}/refunds",
    summary="获取订单退款记录",
)
@apply_rate_limit("60/minute")
def list_refunds(
    request: Request,
    order_uuid: UUID,
    current_user = Depends(AuthControl.is_authed),
) -> ApiResponse[list[OrderRefundResponse]]:
    """
    获取订单退款记录
    """
    refunds = order_refund_service.list_refunds(order_uuid)
    refund_responses = [OrderRefundResponse.model_validate(r) for r in refunds]
    return ApiResponse(code=20000, data=refund_responses)
