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


class Role(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin):
    """统一角色表 - 支持平台级和租户级角色"""
    __tablename__ = "iam_role"
    __table_args__ = (
        UniqueConstraint('code', name='uq_role_code'),
        UniqueConstraint('tenant_id', 'code', name='uq_role_tenant_code'),
    )

    name = Column(String(50), nullable=False, comment="角色名称")
    code = Column(String(50), nullable=False, index=True, comment="角色编码（唯一）")
    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=True, index=True, comment="租户ID（平台角色为NULL）")

    role_subjects = relationship("RoleSubject", back_populates="role", cascade="all, delete-orphan")
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
