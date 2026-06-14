from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    and_,
)
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, EnableStatusMixin, RemarkMixin, SoftDeleteMixin, TimestampMixin, UUIDModel


class TenantMember(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, EnableStatusMixin, UUIDModel):
    """租户成员模型 - 用户与租户的关联关系

    用于管理用户在不同租户中的成员资格。
    subject_id 用于统一RBAC体系中的主体标识。
    """
    __tablename__ = "tenant_member"

    user_id = Column(BigInteger, ForeignKey("iam_user.id"), nullable=False, index=True, comment="用户ID")
    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    subject_id = Column(BigInteger, nullable=False, index=True, comment="统一RBAC主体ID（用于权限关联）")
    is_owner = Column(Boolean, default=False, nullable=False, comment="是否为租户创建人")
    # status 字段由 EnableStatusMixin 提供
    joined_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False, comment="加入时间")
    last_login_at = Column(DateTime(timezone=True), nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    is_muted = Column(Boolean, default=False, nullable=False, comment="禁言状态")
    muted_until = Column(DateTime(timezone=True), nullable=True, comment="禁言结束时间")
    contact_info = Column(String(255), nullable=True, comment="联系方式")

    created_by_member_id = Column(BigInteger, ForeignKey("tenant_member.id"), nullable=True, index=True, comment="创建者成员ID")

    join_type = Column(Integer, nullable=True, index=True, comment="加入方式：0=定向邀请 1=公开链接 2=自助申请")
    audit_status = Column(Integer, default=0, comment="审核状态：0待审核 1通过 2拒绝")

    __table_args__ = (
        UniqueConstraint('user_id', 'tenant_id', name='uq_tenant_member'),
        UniqueConstraint('subject_id', name='uq_tenant_member_subject_id'),
    )

    user = relationship("User", back_populates="tenant_memberships")
    tenant = relationship("Tenant", back_populates="memberships")
    created_by = relationship("TenantMember", remote_side="TenantMember.id", backref="created_sub_accounts")
    role_subjects = relationship("RoleSubject", viewonly=True, primaryjoin="and_(RoleSubject.subject_type==1, foreign(RoleSubject.subject_id)==TenantMember.subject_id)")

