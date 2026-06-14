from sqlalchemy import BigInteger, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import (
    BaseModel,
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    SystemMixin,
    TimestampMixin,
)


class TenantDictType(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin, EnableStatusMixin):
    """租户字典类型模型"""
    __tablename__ = "tenant_dict_type"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_tenant_dict_type_code"),)

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    name = Column(String(50), nullable=False, comment="字典名称")
    code = Column(String(50), nullable=False, index=True, comment="字典编码")

    tenant = relationship("Tenant", back_populates="dict_types")
