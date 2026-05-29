from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, RemarkMixin, SoftDeleteMixin, TimestampMixin


class TenantConfig(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """租户个性化配置模型"""
    __tablename__ = "tenant_config"

    tenant_id = Column(Integer, ForeignKey("tenant.id"), nullable=False, unique=True, index=True, comment="租户ID")

    logo = Column(String(500), nullable=True, comment="租户Logo URL")
    name = Column(String(100), nullable=True, comment="自定义租户名称")
    login_title = Column(String(200), nullable=True, comment="登录页面标题")
    background_color = Column(String(20), nullable=True, comment="背景色")
    background_image = Column(String(500), nullable=True, comment="背景图片URL")
    theme = Column(String(20), default="light", comment="主题：light/dark")
    primary_color = Column(String(20), nullable=True, comment="主题色")

    copyright = Column(String(500), nullable=True, comment="版权信息")
    policy_url = Column(String(500), nullable=True, comment="政策链接")
    service_url = Column(String(500), nullable=True, comment="客服链接")

    enable_register = Column(Integer, default=1, comment="是否允许自主注册：0=否，1=是")
    enable_forget_password = Column(Integer, default=1, comment="是否允许忘记密码：0=否，1=是")

    tenant = relationship("Tenant", backref="config")
