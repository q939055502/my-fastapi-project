from sqlalchemy import BigInteger, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import (
    BaseModel,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    SystemMixin,
    TimestampMixin,
)

from .associations import role_permission_association


class Permission(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin):
    """平台权限表"""
    __tablename__ = "iam_permission"

    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), nullable=False, index=True, comment="权限编码（唯一，格式：资源:操作）")
    type = Column(String(20), nullable=False, index=True, comment="权限类型：menu/button/api")
    parent_id = Column(BigInteger, ForeignKey("iam_permission.id"), nullable=True, index=True, comment="父级权限ID")
    scope = Column(String(20), nullable=False, default="platform", index=True, comment="作用域：platform=平台级，tenant=租户级")

    __table_args__ = (
        UniqueConstraint('code', name='uq_permission_code'),
    )

    parent = relationship("Permission", remote_side="Permission.id")
    children = relationship("Permission", back_populates="parent")
    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")
