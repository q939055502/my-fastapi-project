from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderCreate(BaseModel):
    """订单创建请求"""

    buyer_type: str = Field(..., description="购买主体类型:tenant/user")
    buyer_id: int = Field(..., description="购买主体ID")
    product_type: str = Field(..., description="商品类型:member/service")
    product_id: int = Field(..., description="商品ID")
    cycle_type: str | None = Field(None, description="周期类型:month/year")
    order_type: str = Field(default="new", description="订单类型:new/renew/upgrade")
    original_amount: int = Field(default=0, description="原价(分)")
    discount_amount: int = Field(default=0, description="优惠金额(分)")
    pay_amount: int = Field(default=0, description="实付金额(分)")
    source: str = Field(default="manual", description="订单来源")
    extra_params: dict[str, Any] | None = Field(None, description="扩展参数")
    remark: str | None = Field(None, description="备注")


class OrderUpdate(BaseModel):
    """订单更新请求"""

    pay_amount: int | None = Field(None, description="实付金额(分)")
    discount_amount: int | None = Field(None, description="优惠金额(分)")
    pay_status: str | None = Field(None, description="支付状态")
    order_status: str | None = Field(None, description="订单状态")
    extra_params: dict[str, Any] | None = Field(None, description="扩展参数")
    remark: str | None = Field(None, description="备注")


class OrderResponse(BaseModel):
    """订单响应"""

    id: int
    uuid: UUID
    order_no: str
    buyer_type: str
    buyer_id: int
    product_type: str
    product_id: int
    cycle_type: str | None
    order_type: str
    original_amount: int
    discount_amount: int
    pay_amount: int
    pay_status: str
    order_status: str
    source: str
    extra_params: dict[str, Any] | None
    remark: str | None
    created_at: datetime | None
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    """订单列表项"""

    id: int
    uuid: UUID
    order_no: str
    buyer_type: str
    buyer_id: int
    product_type: str
    product_id: int
    order_type: str
    pay_amount: int
    pay_status: str
    order_status: str
    source: str
    created_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class OrderCancelRequest(BaseModel):
    """取消订单请求"""

    reason: str | None = Field(None, max_length=200, description="取消原因")


class OrderPayRequest(BaseModel):
    """订单支付请求"""

    payment_method: str = Field(..., description="支付方式:wechat/alipay/manual/bank_transfer")
    payer_name: str | None = Field(None, description="付款人姓名")
    payer_account: str | None = Field(None, description="付款人账号")
