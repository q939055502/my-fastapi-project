from sqlalchemy import Column, String, Integer, DateTime
from src.models.base import BaseModel, TimestampMixin


class LoginLog(BaseModel, TimestampMixin):
    """登录日志模型"""
    __tablename__ = "login_log"
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(Integer, nullable=True, index=True, comment="用户ID")
    username = Column(String(64), nullable=False, index=True, comment="用户名")
    
    status = Column(Integer, nullable=False, comment="登录状态（1=成功，0=失败）")
    ip = Column(String(50), nullable=True, index=True, comment="登录IP")
    location = Column(String(200), nullable=True, comment="登录地点")
    device = Column(String(100), nullable=True, comment="设备信息")
    browser = Column(String(100), nullable=True, comment="浏览器")
    os = Column(String(100), nullable=True, comment="操作系统")
    
    msg = Column(String(500), nullable=True, comment="提示消息")
    login_time = Column(DateTime(timezone=True), nullable=False, index=True, comment="登录时间")
    logout_time = Column(DateTime(timezone=True), nullable=True, comment="登出时间")
    
    tenant_id = Column(Integer, nullable=True, index=True, comment="租户ID")
