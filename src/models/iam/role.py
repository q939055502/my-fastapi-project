from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import (
    BaseModel,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    SystemMixin,
    TimestampMixin,
)

from .associations import (
    role_permission_association,
    user_role_association,
)


class Role(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin):
    """平台角色表"""
    __tablename__ = "iam_role"
    __table_args__ = (
        UniqueConstraint('code', name='uq_role_code'),
    )

    name = Column(String(50), nullable=False, comment="角色名称")
    code = Column(String(50), nullable=False, index=True, comment="角色编码（唯一）")

    users = relationship("User", secondary=user_role_association, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")
