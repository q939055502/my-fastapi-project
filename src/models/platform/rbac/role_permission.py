from sqlalchemy import BigInteger, Column, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import ResourceOwnerMixin, TimestampMixin


class RolePermission(BaseModel, TimestampMixin, ResourceOwnerMixin):
    """角色-权限关联表"""
    __tablename__ = "iam_role_permission"

    role_id = Column(BigInteger, nullable=False, index=True, comment="角色ID")
    permission_id = Column(BigInteger, nullable=False, index=True, comment="权限ID")

    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
