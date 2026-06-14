from sqlalchemy import JSON, Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import (
    BaseModel,
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    TimestampMixin,
    UUIDModel,
)


class TenantPlan(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, EnableStatusMixin, UUIDModel):
    """会员套餐模板"""
    __tablename__ = "tenant_plan"

    name = Column(String(50), nullable=False, comment="套餐名称")
    code = Column(String(50), unique=True, nullable=False, index=True, comment="套餐编码")

    price_month = Column(Integer, comment="月费（分）")
    price_quarter = Column(Integer, comment="季费（分）")
    price_year = Column(Integer, comment="年费（分）")

    max_users = Column(Integer, comment="最大用户数（null=无限制）")
    max_depts = Column(Integer, comment="最大部门数（null=无限制）")
    max_storage = Column(Integer, comment="最大存储空间（MB，null=无限制）")
    max_file_size = Column(Integer, comment="单文件最大大小（MB，null=无限制）")
    max_bandwidth = Column(Integer, comment="月带宽限制（GB，null=无限制）")

    available_modules = Column(JSON, nullable=True, comment="可用模块白名单")
    available_features = Column(JSON, nullable=True, comment="可用功能白名单")

    is_auto_approve = Column(Boolean, default=False, comment="是否自动通过")

    quotas = relationship("TenantQuota", back_populates="plan")