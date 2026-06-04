from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, SoftDeleteMixin, TimestampMixin


class UserBind(BaseModel, TimestampMixin, SoftDeleteMixin):
    """用户绑定模型 - 手机号/邮箱与账号的绑定关系"""
    __tablename__ = "iam_user_bind"

    user_id = Column(BigInteger, ForeignKey("iam_user.id"), nullable=False, index=True, comment="用户ID")
    bind_type = Column(Integer, nullable=False, index=True, comment="绑定类型：0=手机号，1=邮箱")
    value = Column(String(255), nullable=False, index=True, comment="绑定值（手机号/邮箱）")
    is_default = Column(Integer, default=0, comment="是否默认登录：0=否，1=是")
    status = Column(String(20), default="pending", comment="状态：pending/verified/disabled")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="验证时间")
    source = Column(String(20), default="manual", comment="创建来源：register/manual/import")

    __table_args__ = (
        UniqueConstraint('user_id', 'bind_type', 'value', name='uq_user_bind'),
    )

    user = relationship("User", back_populates="binds")
