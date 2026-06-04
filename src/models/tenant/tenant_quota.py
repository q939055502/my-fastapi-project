from datetime import UTC, datetime

from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, SoftDeleteMixin, TimestampMixin


class TenantQuota(BaseModel, TimestampMixin, SoftDeleteMixin):
    """租户当前生效配额"""
    __tablename__ = "tenant_quota"

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, unique=True, index=True, comment="租户ID（会员互斥唯一约束）")
    plan_id = Column(BigInteger, ForeignKey("tenant_plan.id"), nullable=True, index=True, comment="套餐ID")

    cycle_type = Column(String(20), nullable=True, index=True, comment="计费周期：month/quarter/year")
    valid_from = Column(DateTime(timezone=True), nullable=True, comment="会员生效开始时间")
    valid_until = Column(DateTime(timezone=True), nullable=True, comment="会员到期时间")

    max_users = Column(Integer, nullable=True, comment="最大用户数（null=无限制）")
    max_depts = Column(Integer, nullable=True, comment="最大部门数（null=无限制）")
    max_storage = Column(Integer, nullable=True, comment="最大存储空间（MB，null=无限制）")
    max_file_size = Column(Integer, nullable=True, comment="单文件最大大小（MB，null=无限制）")
    max_bandwidth = Column(Integer, nullable=True, comment="月带宽限制（GB，null=无限制）")

    available_modules = Column(JSON, nullable=True, comment="可用模块白名单")
    available_features = Column(JSON, nullable=True, comment="可用功能白名单")

    is_free = Column(Integer, default=1, comment="是否免费版：0=否，1=是")

    tenant = relationship("Tenant", back_populates="quota")
    plan = relationship("TenantPlan", back_populates="quotas")

    def is_valid(self) -> bool:
        """判断会员是否有效"""
        if self.is_deleted:
            return False
        if not self.valid_until:
            return True
        return datetime.now(UTC) <= self.valid_until
