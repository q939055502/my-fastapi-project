from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, RemarkMixin, SoftDeleteMixin, TimestampMixin


class TenantPlan(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """租户套餐模型"""
    __tablename__ = "tenant_plan"

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

    def get_price_display(self) -> str:
        """获取格式化的价格显示"""
        if self.price is None:
            return "免费"
        return f"{self.price / 100:.2f} 元"


class Tenant(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """租户模型 - 独立存在，有专属户主"""
    __tablename__ = "tenant"

    name = Column(String(100), nullable=False, comment="租户名称")
    code = Column(String(50), unique=True, nullable=False, index=True, comment="租户编码")
    plan_id = Column(Integer, ForeignKey("tenant_plan.id"), nullable=False, comment="套餐ID")
    owner_user_id = Column(Integer, ForeignKey("iam_user.id"), nullable=False, comment="户主用户ID")
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

    memberships = relationship("TenantMember", back_populates="tenant", cascade="all, delete-orphan")

    def is_trial_period(self) -> bool:
        """判断是否处于试用期"""
        if not self.trial_start_date or not self.trial_end_date:
            return False
        now = datetime.now(UTC)
        return self.trial_start_date <= now <= self.trial_end_date

    def is_expired(self) -> bool:
        """判断租户是否过期"""
        if not self.expire_date:
            return False
        return datetime.now(UTC) > self.expire_date

    def is_active_tenant(self) -> bool:
        """判断租户是否处于活跃状态"""
        return self.status == "active" and not self.is_deleted and not self.is_expired()
