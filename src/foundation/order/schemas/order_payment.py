from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderPaymentCreate(BaseModel):
    """订单支付记录创建"""

    order_id: int = Field(..., description="订单ID")
    payment_method: str = Field(..., description="支付方式")
    payment_no: str | None = Field(None, description="支付流水号")
    amount: int = Field(..., description="支付金额(分)")
    payer_name: str | None = Field(None, description="付款人姓名")
    payer_account: str | None = Field(None, description="付款人账号")
    callback_data: dict[str, Any] | None = Field(None, description="支付平台回调数据")
    remark: str | None = Field(None, description="备注")


class OrderPaymentResponse(BaseModel):
    """订单支付记录响应"""

    id: int
    uuid: UUID
    order_id: int
    payment_method: str
    payment_no: str | None
    amount: int
    status: str
    paid_at: datetime | None
    payer_name: str | None
    payer_account: str | None
    created_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
