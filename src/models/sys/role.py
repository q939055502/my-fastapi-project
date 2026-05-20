from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from src.models.base import BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin
from .associations import user_role_association, role_resource_association


class Role(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """角色模型"""
    __tablename__ = "role"
    __table_args__ = (
        UniqueConstraint('name', 'tenant_id', name='uq_role_name_tenant'),
        {'extend_existing': True}
    )

    name = Column(String(20), nullable=False, comment="角色名称")
    tenant_id = Column(Integer, nullable=True, comment="租户ID（null=系统级）")
    is_system = Column(Boolean, default=False, nullable=False, comment="系统内置角色，创建后不可修改")

    users = relationship("User", secondary=user_role_association, back_populates="roles")
    resources = relationship("Resource", secondary=role_resource_association, back_populates="roles")
