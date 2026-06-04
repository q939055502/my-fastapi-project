from datetime import UTC, datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from src.models.base import (
    BaseModel,
    RemarkMixin,
    SoftDeleteMixin,
    TenantStatusMixin,
    TimestampMixin,
)


class Tenant(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, TenantStatusMixin):
    """租户模型 - 独立存在，有专属户主"""
    __tablename__ = "tenant"

    name = Column(String(100), nullable=False, comment="租户名称")
    code = Column(String(50), unique=True, nullable=False, index=True, comment="租户编码")
    owner_user_id = Column(BigInteger, ForeignKey("iam_user.id"), nullable=False, comment="户主用户ID")

    contact_name = Column(String(50), nullable=True, comment="联系人姓名")
    contact_phone = Column(String(20), nullable=True, comment="联系人电话")
    contact_email = Column(String(100), nullable=True, comment="联系人邮箱")

    company_size = Column(String(50), nullable=True, comment="公司规模")
    industry = Column(String(50), nullable=True, comment="行业")

    trial_start_date = Column(DateTime(timezone=True), nullable=True, comment="试用开始时间")
    trial_end_date = Column(DateTime(timezone=True), nullable=True, comment="试用结束时间")

    logo = Column(String(500), nullable=True, comment="租户Logo")

    owner_user = relationship("User", foreign_keys=[owner_user_id], backref="owned_tenants")
    quota = relationship("TenantQuota", back_populates="tenant", uselist=False, cascade="all, delete-orphan")
    memberships = relationship("TenantMember", back_populates="tenant", cascade="all, delete-orphan")
    usages = relationship("TenantUsage", back_populates="tenant", cascade="all, delete-orphan")
    hourly_usages = relationship("TenantHourlyUsage", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("TenantRole", back_populates="tenant", cascade="all, delete-orphan")
    permissions = relationship("TenantPermission", back_populates="tenant", cascade="all, delete-orphan")
    invites = relationship("TenantInvite", back_populates="tenant", cascade="all, delete-orphan")

    def is_trial_period(self) -> bool:
        """判断是否处于试用期"""
        if not self.trial_start_date or not self.trial_end_date:
            return False
        now = datetime.now(UTC)
        return self.trial_start_date <= now <= self.trial_end_date

    def is_active_tenant(self) -> bool:
        """判断租户是否处于活跃状态"""
        if self.status != "active" or self.is_deleted:
            return False
        if self.quota:
            return self.quota.is_valid()
        return True
