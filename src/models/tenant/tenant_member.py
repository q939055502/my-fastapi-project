from datetime import datetime

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

from src.models.base import BaseModel, RemarkMixin, SoftDeleteMixin, TimestampMixin

from .associations import tenant_member_role_association


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
    is_owner = Column(Integer, default=0, nullable=False, comment="是否为租户创建人：0=否，1=是")
    role = Column(String(50), default="member", nullable=False, comment="租户内角色")
    joined_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False, comment="加入时间")

    is_sub_account = Column(Integer, default=0, nullable=False, comment="是否为租户创建的子账号（属于租户资产）：0=否，1=是")
    created_by_member_id = Column(BigInteger, ForeignKey("tenant_member.id"), nullable=True, index=True, comment="创建者成员ID")

    join_type = Column(String(16), nullable=True, index=True, comment="加入方式：invite(定向邀请)/public(公开链接)/apply(自助申请)")
    audit_status = Column(Integer, default=0, comment="审核状态：0待审核 1通过 2拒绝")
    invite_id = Column(BigInteger, ForeignKey("tenant_invite.id"), nullable=True, index=True, comment="关联的邀请/申请ID")

    __table_args__ = (
        UniqueConstraint('user_id', 'tenant_id', name='uq_tenant_member'),
    )

    user = relationship("User", back_populates="tenant_memberships")
    tenant = relationship("Tenant", back_populates="memberships")
    created_by = relationship("TenantMember", remote_side="TenantMember.id", backref="created_sub_accounts")
    roles = relationship("TenantRole", secondary=tenant_member_role_association, back_populates="members")
    invite = relationship("TenantInvite", back_populates="members")

    def get_identity_label(self) -> str:
        """获取身份标签"""
        if self.is_owner == 1:
            return "租户创建人"
        elif self.is_sub_account == 1:
            return "子账号"
        return "外部成员"
