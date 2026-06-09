from sqlalchemy import BigInteger, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, TimestampMixin


class RolePermission(BaseModel, TimestampMixin):
    """角色-权限关联表"""
    __tablename__ = "iam_role_permission"

    role_id = Column(BigInteger, ForeignKey("iam_role.id", ondelete="CASCADE"), nullable=False, index=True, comment="角色ID")
    permission_id = Column(BigInteger, ForeignKey("iam_permission.id", ondelete="CASCADE"), nullable=False, index=True, comment="权限ID")
    created_by = Column(BigInteger, comment="分配人ID")

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )

    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
