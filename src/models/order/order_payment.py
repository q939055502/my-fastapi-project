from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel
from src.models.mixins import RemarkMixin, SoftDeleteMixin, TimestampMixin


class OrderPayment(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """订单支付记录模型"""
    __tablename__ = "order_payment"

    order_id = Column(BigInteger, ForeignKey("order_info.id"), nullable=False, index=True, comment="订单ID")

    payment_method = Column(String(20), nullable=False, comment="支付方式：wechat/alipay/manual/bank_transfer")
    payment_no = Column(String(100), nullable=True, unique=True, index=True, comment="支付流水号/交易号")

    amount = Column(Integer, nullable=False, comment="支付金额（分）")

    status = Column(String(20), default="pending", nullable=False, index=True, comment="支付状态：pending/success/failed/refunded")
    paid_at = Column(DateTime(timezone=True), nullable=True, comment="支付成功时间")

    payer_name = Column(String(50), nullable=True, comment="付款人姓名")
    payer_account = Column(String(100), nullable=True, comment="付款人账号")

    callback_data = Column(JSON, nullable=True, comment="支付平台原始回调数据")

    order = relationship("OrderInfo", back_populates="payments")
    refunds = relationship("OrderRefund", back_populates="order_payment", cascade="all, delete-orphan")