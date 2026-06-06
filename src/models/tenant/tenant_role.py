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

from .associations import tenant_role_permission_association


class TenantRole(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin):
    """租户角色表"""

    __tablename__ = "tenant_role"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_tenant_role_code"),)

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    name = Column(String(50), nullable=False, comment="角色名称")
    code = Column(String(50), nullable=False, index=True, comment="角色编码（唯一）")

    tenant = relationship("Tenant", back_populates="roles")
    role_members = relationship("TenantMemberRole", back_populates="tenant_role", cascade="all, delete-orphan")
    permissions = relationship(
        "TenantPermission", secondary=tenant_role_permission_association, back_populates="roles"
    )
