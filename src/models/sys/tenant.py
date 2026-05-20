from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from src.models.base import BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin
from .associations import user_tenant_association


class TenantPlan(BaseModel, TimestampMixin, SoftDeleteMixin):
    """租户套餐模型"""
    __tablename__ = "tenant_plan"
    __table_args__ = {'extend_existing': True}

    name = Column(String(50), nullable=False, comment="套餐名称")
    code = Column(String(50), unique=True, nullable=False, comment="套餐编码")
    is_auto_approve = Column(Integer, default=0, comment="是否自动通过：0=否，1=是")
    max_users = Column(Integer, comment="最大用户数")
    max_depts = Column(Integer, comment="最大部门数")
    max_storage = Column(Integer, comment="最大存储空间（MB）")
    max_file_size = Column(Integer, comment="单文件最大大小（MB）")
    price = Column(Integer, comment="价格（分）")
    features = Column(Text, comment="功能特性描述")
    available_modules = Column(String(500), comment="可用模块列表")
    status = Column(Integer, default=1, comment="1启用 0禁用")
    sort = Column(Integer, default=0, comment="排序")


class Tenant(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """租户模型 - 独立存在，有专属户主"""
    __tablename__ = "tenant"
    __table_args__ = {'extend_existing': True}
    
    name = Column(String(100), nullable=False, comment="租户名称")
    code = Column(String(50), unique=True, nullable=False, index=True, comment="租户编码")
    plan_id = Column(Integer, ForeignKey("tenant_plan.id"), nullable=False, comment="套餐ID")
    owner_user_id = Column(Integer, ForeignKey("user.id"), nullable=False, comment="户主用户ID")
    status = Column(String(20), default="active", comment="状态：active/suspended/trial/expired")

    contact_name = Column(String(50), nullable=True, comment="联系人姓名")
    contact_phone = Column(String(20), nullable=True, comment="联系人电话")
    contact_email = Column(String(100), nullable=True, comment="联系人邮箱")

    company_size = Column(String(50), nullable=True, comment="公司规模")
    industry = Column(String(50), nullable=True, comment="行业")

    trial_start_date = Column(DateTime(timezone=True), nullable=True, comment="试用开始时间")
    trial_end_date = Column(DateTime(timezone=True), nullable=True, comment="试用结束时间")
    expire_date = Column(DateTime(timezone=True), nullable=True, comment="到期时间")

    logo = Column(String(500), nullable=True, comment="租户Logo")

    owner_user = relationship("User", foreign_keys=[owner_user_id], backref="owned_tenants")
    plan = relationship("TenantPlan")
    members = relationship("User", secondary=user_tenant_association, back_populates="tenants")
