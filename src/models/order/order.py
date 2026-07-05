from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel
from src.models.mixins import (
    RemarkMixin,
    ResourceOrgMixin,
    ResourceOwnerMixin,
    SoftDeleteMixin,
    SortMixin,
    TimestampMixin,
)


class OrderInfo(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, ResourceOwnerMixin, ResourceOrgMixin):
    """订单模型"""
    __tablename__ = "order_info"

    order_no = Column(String(50), unique=True, nullable=False, index=True, comment="订单号")

    buyer_type = Column(String(20), nullable=False, index=True, comment="购买主体类型:tenant/user")
    buyer_id = Column(Integer, nullable=False, index=True, comment="购买主体ID:租户ID/用户ID")

    product_type = Column(String(20), nullable=False, index=True, comment="商品类型:member/service")
    product_id = Column(Integer, nullable=False, index=True, comment="商品ID:套餐ID/服务ID")

    cycle_type = Column(String(20), nullable=True, index=True, comment="周期类型:month/year(仅会员套餐使用)")
    order_type = Column(String(20), default="new", nullable=False, index=True, comment="订单类型:new/renew/upgrade")

    original_amount = Column(Integer, default=0, comment="原价(分)")
    discount_amount = Column(Integer, default=0, comment="优惠金额(分)")
    pay_amount = Column(Integer, default=0, comment="实付金额(分)")

    pay_status = Column(String(20), default="pending", nullable=False, index=True, comment="支付状态:pending/paid/cancelled/refunded/expired")
    order_status = Column(String(20), default="pending", nullable=False, index=True, comment="订单状态:pending/processing/completed/cancelled")
    source = Column(String(20), default="manual", comment="订单来源:manual/auto/trial_upgrade")

    extra_params = Column(JSON, nullable=True, comment="扩展参数")

    payments = relationship("OrderPayment", back_populates="order", cascade="all, delete-orphan")
    refunds = relationship("OrderRefund", back_populates="order", cascade="all, delete-orphan")
    logs = relationship("OrderLog", back_populates="order", cascade="all, delete-orphan")
