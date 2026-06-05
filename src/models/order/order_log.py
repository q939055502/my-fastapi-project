from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, RemarkMixin, SoftDeleteMixin, TimestampMixin


class OrderLog(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """订单操作日志模型"""
    __tablename__ = "order_log"

    order_id = Column(BigInteger, ForeignKey("order.id"), nullable=False, index=True, comment="订单ID")

    operator_type = Column(String(20), default="user", nullable=False, index=True, comment="操作人类型：system/user/admin")
    operator_id = Column(BigInteger, nullable=True, index=True, comment="操作人ID")
    operator_name = Column(String(50), nullable=True, comment="操作人姓名（冗余）")

    action = Column(String(50), nullable=False, index=True, comment="操作动作：create/pay/cancel/refund/expire/extend/upgrade")
    before_pay_status = Column(String(20), nullable=True, comment="操作前支付状态")
    after_pay_status = Column(String(20), nullable=True, comment="操作后支付状态")
    before_order_status = Column(String(20), nullable=True, comment="操作前订单状态")
    after_order_status = Column(String(20), nullable=True, comment="操作后订单状态")

    detail = Column(String(500), nullable=True, comment="操作详情")

    order = relationship("Order", back_populates="logs")
