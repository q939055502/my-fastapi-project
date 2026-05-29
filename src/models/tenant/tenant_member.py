from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, RemarkMixin, SoftDeleteMixin, TimestampMixin


class TenantMember(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """租户成员模型 - 用户与租户的关联关系

    替代原有的 user_tenant_association Table，改为实体模型以便支持业务方法

    身份类型判定：
    - is_owner=True: 租户创建人（自有账号）
    - is_sub_account=True: 租户创建的子账号（属于租户资产）
    - is_owner=False and is_sub_account=False: 外部用户加入租户（自有账号）
    """
    __tablename__ = "tenant_member"

    user_id = Column(BigInteger, ForeignKey("iam_user.id"), nullable=False, index=True, comment="用户ID")
    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    is_owner = Column(Boolean, default=False, nullable=False, comment="是否为租户创建人")
    role = Column(String(50), default="member", nullable=False, comment="租户内角色")
    joined_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False, comment="加入时间")

    is_sub_account = Column(Boolean, default=False, nullable=False, comment="是否为租户创建的子账号（属于租户资产）")
    created_by_member_id = Column(BigInteger, ForeignKey("tenant_member.id"), nullable=True, index=True, comment="创建者成员ID")

    __table_args__ = (
        UniqueConstraint('user_id', 'tenant_id', name='uq_tenant_member'),
    )

    user = relationship("User", back_populates="tenant_memberships")
    tenant = relationship("Tenant", back_populates="memberships")
    created_by = relationship("TenantMember", remote_side="TenantMember.id", backref="created_sub_accounts")

    def get_identity_label(self) -> str:
        """获取身份标签"""
        if self.is_owner:
            return "租户创建人"
        elif self.is_sub_account:
            return "子账号"
        return "外部成员"
