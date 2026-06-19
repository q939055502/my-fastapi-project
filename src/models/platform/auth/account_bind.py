from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String

from src.models.base import BaseModel
from src.models.mixins import SoftDeleteMixin, TimestampMixin, UUIDModel


class AccountBind(BaseModel, TimestampMixin, SoftDeleteMixin, UUIDModel):
    """账号绑定模型 - 手机号/邮箱与用户账号的绑定关系

    支持一个手机号/邮箱绑定多个用户账号,实现多账号绑定同个身份标识的场景"""
    __tablename__ = "iam_account_bind"

    user_id = Column(BigInteger, nullable=False, index=True, comment="用户ID")
    bind_type = Column(Integer, nullable=False, index=True, comment="绑定类型:0=手机号,1=邮箱")
    identifier = Column(String(255), nullable=False, index=True, comment="绑定标识(手机号/邮箱)")
    is_default = Column(Boolean, default=False, comment="是否默认登录")
    status = Column(String(20), default="pending", comment="状态:pending/verified/disabled")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="验证时间")
    source = Column(String(20), default="manual", comment="创建来源:register/manual/import")
