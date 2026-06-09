from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, RemarkMixin, SoftDeleteMixin, TimestampMixin


class OrderRefund(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """订单退款记录模型"""
    __tablename__ = "order_refund"

    order_id = Column(BigInteger, ForeignKey("order_info.id"), nullable=False, index=True, comment="订单ID")
    order_payment_id = Column(BigInteger, ForeignKey("order_payment.id"), nullable=True, index=True, comment="支付记录ID")

    refund_no = Column(String(50), nullable=True, unique=True, index=True, comment="退款单号")
    refund_method = Column(String(20), nullable=False, comment="退款方式：original/alipay/wechat/other")
    refund_amount = Column(Integer, nullable=False, comment="退款金额（分）")

    status = Column(String(20), default="pending", nullable=False, index=True, comment="退款状态：pending/processing/success/failed")
    reason = Column(String(200), nullable=True, comment="退款原因")

    operator_type = Column(String(20), default="user", nullable=False, index=True, comment="操作人类型：system/user/admin")
    operator_id = Column(BigInteger, nullable=True, index=True, comment="操作人ID")
    operator_name = Column(String(50), nullable=True, comment="操作人姓名（冗余）")

    refunded_at = Column(DateTime(timezone=True), nullable=True, comment="退款成功时间")
    callback_data = Column(JSON, nullable=True, comment="支付平台原始退款回调数据")

    order = relationship("OrderInfo", back_populates="refunds")
    order_payment = relationship("OrderPayment", back_populates="refunds")
