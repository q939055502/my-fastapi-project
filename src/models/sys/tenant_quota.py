from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.models.base import BaseModel, TimestampMixin, SoftDeleteMixin


class TenantQuota(BaseModel, TimestampMixin, SoftDeleteMixin):
    """租户配额模型"""
    __tablename__ = "tenant_quota"
    __table_args__ = {'extend_existing': True}
    
    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False, unique=True, index=True, comment="租户ID")
    
    max_users = Column(Integer, nullable=True, comment="最大用户数（null=无限制）")
    max_depts = Column(Integer, nullable=True, comment="最大部门数（null=无限制）")
    max_storage = Column(Integer, nullable=True, comment="最大存储空间（MB）")
    max_file_size = Column(Integer, nullable=True, comment="单文件最大大小（MB）")
    max_bandwidth = Column(Integer, nullable=True, comment="月带宽限制（GB）")
    
    available_modules = Column(JSON, nullable=True, comment="可用模块列表")
    available_features = Column(JSON, nullable=True, comment="可用功能列表")
    
    current_users = Column(Integer, default=0, comment="当前用户数")
    current_storage = Column(Integer, default=0, comment="当前已用存储（MB）")
    
    reset_date = Column(String(20), nullable=True, comment="配额重置日期（如每月1日）")
    is_overdue = Column(Integer, default=0, comment="是否过期：0=否，1=是")
    
    tenant = relationship("Tenant", backref="quota")
