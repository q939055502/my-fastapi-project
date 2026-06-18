from sqlalchemy import BigInteger, Column, String

from src.models.base import BaseModel
from src.models.mixins import RemarkMixin, TimestampMixin


class Config(BaseModel, TimestampMixin, RemarkMixin):
    """租户个性化配置模型"""
    __tablename__ = "platform_config"

    tenant_id = Column(BigInteger, nullable=False, unique=True, index=True, comment="租户ID")

    logo = Column(String(500), nullable=True, comment="租户Logo URL")
    name = Column(String(100), nullable=True, comment="自定义租户名称")
    login_title = Column(String(200), nullable=True, comment="登录页面标题")
    background_color = Column(String(20), nullable=True, comment="背景色")
    background_image = Column(String(500), nullable=True, comment="背景图片URL")
    theme = Column(String(20), default="light", comment="主题：light/dark")
    primary_color = Column(String(20), nullable=True, comment="主题色")

    contact_name = Column(String(50), nullable=True, comment="联系人")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    contact_address = Column(String(500), nullable=True, comment="地址")
    contact_email = Column(String(100), nullable=True, comment="邮箱")

    copyright = Column(String(500), nullable=True, comment="版权信息")
    policy_url = Column(String(500), nullable=True, comment="政策链接")
    service_url = Column(String(500), nullable=True, comment="客服链接")
