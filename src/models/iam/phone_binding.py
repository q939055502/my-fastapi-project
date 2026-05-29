from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, RemarkMixin, SoftDeleteMixin, TimestampMixin


class PhoneBinding(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """手机号绑定模型

    1个手机号可以绑定1个自有账号（主绑定）和多个成员账号（次绑定）
    """
    __tablename__ = "phone_binding"

    phone = Column(String(20), unique=True, nullable=False, index=True, comment="手机号码")
    user_id = Column(Integer, ForeignKey("iam_user.id"), nullable=False, index=True, comment="用户ID")
    is_primary = Column(Boolean, default=True, comment="是否主绑定（自有账号）")
    verified_at = Column(DateTime(timezone=True), nullable=True, comment="验证时间")

    user = relationship("User", backref="phone_bindings")



# 确保「1 手机号仅 1 个主绑定」：UniqueConstraint('phone', 'is_primary', name='uq_phone_primary')（仅限制 is_primary=True 时 phone 唯一）。
