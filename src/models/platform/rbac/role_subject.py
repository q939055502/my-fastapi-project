from sqlalchemy import BigInteger, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, TimestampMixin


class RoleSubject(BaseModel, TimestampMixin):
    """角色-主体关联表（统一RBAC核心关联表）"""
    __tablename__ = "iam_role_subject"

    subject_id = Column(BigInteger, nullable=False, index=True, comment="主体ID（用户ID或成员ID）")
    subject_type = Column(Integer, nullable=False, index=True, comment="主体类型：0=平台用户，1=租户成员")
    role_id = Column(BigInteger, ForeignKey("iam_role.id"), nullable=False, index=True, comment="角色ID")
    created_by = Column(BigInteger, comment="创建人ID")

    __table_args__ = (
        UniqueConstraint('subject_id', 'subject_type', 'role_id', name='uq_role_subject'),
    )

    role = relationship("Role", back_populates="role_subjects")
