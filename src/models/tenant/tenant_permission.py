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


class TenantPermission(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin):
    """租户权限表"""

    __tablename__ = "tenant_permission"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_tenant_permission_code"),)

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    name = Column(String(50), nullable=False, comment="权限名称")
    code = Column(String(100), nullable=False, index=True, comment="权限编码（唯一，格式：资源:操作）")
    type = Column(String(20), nullable=False, index=True, comment="权限类型：menu/button/api")
    parent_id = Column(BigInteger, ForeignKey("tenant_permission.id"), nullable=True, index=True, comment="父级权限ID")

    tenant = relationship("Tenant", back_populates="permissions")
    parent = relationship("TenantPermission", remote_side="TenantPermission.id", back_populates="children")
    children = relationship("TenantPermission", back_populates="parent")
    roles = relationship(
        "TenantRole", secondary=tenant_role_permission_association, back_populates="permissions"
    )
