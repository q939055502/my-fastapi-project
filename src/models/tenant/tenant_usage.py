from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, SoftDeleteMixin, TimestampMixin


class TenantUsage(BaseModel, TimestampMixin, SoftDeleteMixin):
    """租户月度用量记录"""
    __tablename__ = "tenant_usage"

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    usage_month = Column(String(7), nullable=False, index=True, comment="自然月：YYYY-MM")

    current_users = Column(Integer, default=0, comment="当前用户数")
    current_storage = Column(Integer, default=0, comment="当前已用存储（MB）")
    current_bandwidth = Column(Integer, default=0, comment="当月已用带宽（GB）")

    tenant = relationship("Tenant", back_populates="usages")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'usage_month', name='uq_tenant_usage_month'),
    )
