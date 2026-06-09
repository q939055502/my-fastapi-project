from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, EnableStatusMixin, RemarkMixin, SoftDeleteMixin, TimestampMixin


class TenantInvite(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, EnableStatusMixin):
    """租户邀请/申请表 - 统一管理所有邀请和申请"""

    __tablename__ = "tenant_invite"

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    invite_type = Column(String(16), nullable=False, index=True, comment="邀请类型：private(定向邀请)/public(公开链接)/apply(自助申请)")
    invite_code = Column(String(64), nullable=True, unique=True, index=True, comment="邀请码（公开链接/定向邀请用）")

    target_contact = Column(String(100), nullable=True, index=True, comment="目标联系方式（手机号/邮箱，定向邀请用）")
    target_user_id = Column(BigInteger, ForeignKey("iam_user.id"), nullable=True, index=True, comment="目标用户ID（定向邀请用）")

    default_role_id = Column(BigInteger, ForeignKey("iam_role.id"), nullable=True, comment="默认角色ID")
    need_audit = Column(Integer, default=0, comment="是否需要审批：0无需审批 1需要审批")

    apply_user_id = Column(BigInteger, ForeignKey("iam_user.id"), nullable=True, index=True, comment="申请人用户ID（自助申请用）")
    apply_status = Column(Integer, default=0, comment="申请状态：0待审核 1通过 2拒绝")
    audit_member_id = Column(BigInteger, ForeignKey("tenant_member.id"), nullable=True, index=True, comment="审批人成员ID")
    audit_time = Column(BigInteger, nullable=True, comment="审批时间")
    audit_remark = Column(String(500), nullable=True, comment="审批备注")

    creator_member_id = Column(BigInteger, ForeignKey("tenant_member.id"), nullable=True, index=True, comment="创建者成员ID")
    expire_time = Column(BigInteger, nullable=True, index=True, comment="过期时间（时间戳）")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'target_contact', name='uq_tenant_target_contact'),
    )

    tenant = relationship("Tenant", back_populates="invites")
    target_user = relationship("User", foreign_keys=[target_user_id])
    apply_user = relationship("User", foreign_keys=[apply_user_id])
    default_role = relationship("Role")
    audit_member = relationship("TenantMember", foreign_keys=[audit_member_id])
    creator_member = relationship("TenantMember", foreign_keys=[creator_member_id])
