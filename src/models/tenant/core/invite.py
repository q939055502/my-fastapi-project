from sqlalchemy import BigInteger, Boolean, Column, Integer, String, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import EnableStatusMixin, RemarkMixin, SoftDeleteMixin, TimestampMixin, UUIDModel


class Invite(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, EnableStatusMixin, UUIDModel):
    """租户邀请/申请表 - 统一管理所有邀请和申请"""

    __tablename__ = "platform_invite"

    tenant_id = Column(BigInteger, nullable=False, index=True, comment="租户ID")
    invite_type = Column(String(16), nullable=False, index=True, comment="邀请类型：private(定向邀请)/public(公开链接)/apply(自助申请)")
    invite_code = Column(String(64), nullable=True, unique=True, index=True, comment="邀请码（公开链接/定向邀请用）")

    target_contact = Column(String(100), nullable=True, comment="目标联系方式（手机号/邮箱，定向邀请用）")
    target_user_id = Column(BigInteger, nullable=True, comment="目标用户ID（定向邀请用）")

    default_role_id = Column(BigInteger, nullable=True, comment="默认角色ID")
    need_audit = Column(Boolean, default=False, comment="是否需要审批")

    apply_user_id = Column(BigInteger, nullable=True, comment="申请人用户ID（自助申请用）")
    apply_status = Column(Integer, default=0, index=True, comment="申请状态：0待审核 1通过 2拒绝")
    audit_member_id = Column(BigInteger, nullable=True, comment="审批人成员ID")
    audit_time = Column(BigInteger, nullable=True, comment="审批时间")
    audit_remark = Column(String(500), nullable=True, comment="审批备注")

    creator_member_id = Column(BigInteger, nullable=True, comment="创建者成员ID")
    expire_time = Column(BigInteger, nullable=True, index=True, comment="过期时间（时间戳）")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'target_contact', name='uq_platform_invite_contact'),
    )
