from sqlalchemy import BigInteger, Column, DateTime, String

from src.models.base import BaseModel
from src.models.mixins import (
    RemarkMixin,
    SoftDeleteMixin,
    TenantStatusMixin,
    TimestampMixin,
    UUIDModel,
)


class Tenant(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, TenantStatusMixin, UUIDModel):
    """租户模型 - 独立存在,有专属户主"""
    __tablename__ = "platform_tenant"

    name = Column(String(100), nullable=False, comment="租户名称")
    code = Column(String(50), unique=True, nullable=False, index=True, comment="租户编码")
    owner_user_id = Column(BigInteger, nullable=False, comment="户主用户ID")

    contact_name = Column(String(50), nullable=True, comment="联系人姓名")
    contact_phone = Column(String(20), nullable=True, comment="联系人手机号")
    contact_email = Column(String(100), nullable=True, comment="联系人邮箱")

    company_size = Column(String(50), nullable=True, comment="公司规模")
    industry = Column(String(50), nullable=True, comment="行业")

    trial_start_date = Column(DateTime(timezone=True), nullable=True, comment="试用开始时间")
    trial_end_date = Column(DateTime(timezone=True), nullable=True, comment="试用结束时间")

    logo = Column(String(500), nullable=True, comment="租户Logo")
