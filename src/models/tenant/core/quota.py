from sqlalchemy import JSON, BigInteger, Boolean, Column, DateTime, Integer, String

from src.models.base import BaseModel
from src.models.mixins import SoftDeleteMixin, TimestampMixin


class Quota(BaseModel, TimestampMixin, SoftDeleteMixin):
    """租户当前生效配额"""
    __tablename__ = "platform_quota"

    tenant_id = Column(BigInteger, nullable=False, unique=True, index=True, comment="租户ID(会员互斥唯一约束)")
    plan_id = Column(BigInteger, nullable=True, index=True, comment="套餐ID")

    cycle_type = Column(String(20), nullable=True, index=True, comment="计费周期:month/quarter/year")
    valid_from = Column(DateTime(timezone=True), nullable=True, comment="会员生效开始时间")
    valid_until = Column(DateTime(timezone=True), nullable=True, comment="会员到期时间")

    max_users = Column(Integer, nullable=True, comment="最大用户数(null=无限制)")
    max_orgs = Column(Integer, nullable=True, comment="最大组织数(null=无限制)")
    max_storage = Column(Integer, nullable=True, comment="最大存储空间(MB,null=无限制)")
    max_file_size = Column(Integer, nullable=True, comment="单文件最大大小(MB,null=无限制)")
    max_bandwidth = Column(Integer, nullable=True, comment="月带宽限制(GB,null=无限制)")

    available_modules = Column(JSON, nullable=True, comment="可用模块白名单")
    available_features = Column(JSON, nullable=True, comment="可用功能白名单")

    is_free = Column(Boolean, default=True, comment="是否免费版")
