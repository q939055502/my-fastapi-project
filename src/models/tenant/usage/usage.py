from sqlalchemy import Column, Integer, String, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import ResourceOrgMixin, ResourceOwnerMixin, SoftDeleteMixin, TimestampMixin


class Usage(BaseModel, TimestampMixin, SoftDeleteMixin, ResourceOwnerMixin, ResourceOrgMixin):
    """租户月度用量记录"""
    __tablename__ = "platform_usage"

    usage_month = Column(String(7), nullable=False, index=True, comment="自然月:YYYY-MM")

    current_users = Column(Integer, default=0, comment="当前用户数")
    current_storage = Column(Integer, default=0, comment="当前已用存储(MB)")
    current_bandwidth = Column(Integer, default=0, comment="当月已用带宽(GB)")

    __table_args__ = (
        UniqueConstraint('tenant_id', 'usage_month', name='uq_platform_usage_month'),
    )
