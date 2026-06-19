from sqlalchemy import Column, DateTime, Integer, String

from src.models.base import BaseModel
from src.models.mixins import LoginStatusMixin, SoftDeleteMixin, TimestampMixin


class LoginLog(BaseModel, TimestampMixin, SoftDeleteMixin, LoginStatusMixin):
    """登录日志模型"""
    __tablename__ = "sys_login_log"

    user_id = Column(Integer, nullable=True, index=True, comment="用户ID")
    tenant_id = Column(Integer, nullable=True, index=True, comment="租户ID")

    ip = Column(String(50), nullable=True, comment="登录IP")
    location = Column(String(200), nullable=True, comment="登录地点")
    device = Column(String(100), nullable=True, comment="设备信息")
    browser = Column(String(100), nullable=True, comment="浏览器")
    os_name = Column(String(100), nullable=True, comment="操作系统")

    msg = Column(String(500), nullable=True, comment="提示消息")
    login_time = Column(DateTime(timezone=True), nullable=False, index=True, comment="登录时间")
    logout_time = Column(DateTime(timezone=True), nullable=True, comment="登出时间")
