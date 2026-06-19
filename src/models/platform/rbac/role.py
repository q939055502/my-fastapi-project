from sqlalchemy import Column, String, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import (
    RemarkMixin,
    ResourceOwnerMixin,
    SoftDeleteMixin,
    SortMixin,
    SystemMixin,
    TimestampMixin,
    UUIDModel,
)


class Role(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin, UUIDModel, ResourceOwnerMixin):
    """统一角色表 - 支持平台级和租户级角色"""
    __tablename__ = "iam_role"
    __table_args__ = (
        UniqueConstraint('code', name='uq_role_code'),
        UniqueConstraint('tenant_id', 'code', name='uq_role_tenant_code'),
    )

    name = Column(String(50), nullable=False, comment="角色名称")
    code = Column(String(50), nullable=False, index=True, comment="角色编码(唯一标识)")
