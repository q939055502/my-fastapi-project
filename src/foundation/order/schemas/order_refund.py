from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderRefundCreate(BaseModel):
    """订单退款创建"""

    order_id: int = Field(..., description="订单ID")
    order_payment_id: int | None = Field(None, description="支付记录ID")
    refund_method: str = Field(..., description="退款方式")
    refund_amount: int = Field(..., description="退款金额(分)")
    reason: str | None = Field(None, description="退款原因")
    operator_type: str = Field(default="user", description="操作人类型")
    operator_id: int | None = Field(None, description="操作人ID")
    operator_name: str | None = Field(None, description="操作人姓名")
    callback_data: dict[str, Any] | None = Field(None, description="支付平台回调数据")
    remark: str | None = Field(None, description="备注")


class OrderRefundResponse(BaseModel):
    """订单退款响应"""

    id: int
    uuid: UUID
    order_id: int
    order_payment_id: int | None
    refund_no: str | None
    refund_method: str
    refund_amount: int
    status: str
    reason: str | None
    refunded_at: datetime | None
    created_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
