from sqlalchemy import JSON, Column, Integer, String, Text

from src.models.base import BaseModel, TimestampMixin


class AuditLog(BaseModel, TimestampMixin):
    """审计日志模型（全局操作审计）"""
    __tablename__ = "audit_log"

    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    username = Column(String(64), nullable=False, index=True, comment="用户名称")
    tenant_id = Column(Integer, nullable=True, index=True, comment="租户ID")

    module = Column(String(64), default="", index=True, comment="功能模块")
    summary = Column(String(128), default="", index=True, comment="请求描述")
    method = Column(String(10), default="", index=True, comment="请求方法")
    path = Column(String(255), default="", index=True, comment="请求路径")

    status = Column(Integer, default=-1, index=True, comment="状态码")
    response_time = Column(Integer, default=0, index=True, comment="响应时间(单位ms)")

    ip = Column(String(50), nullable=True, index=True, comment="IP地址")
    location = Column(String(200), nullable=True, comment="操作地点")
    device = Column(String(100), nullable=True, comment="设备信息")
    browser = Column(String(100), nullable=True, comment="浏览器")
    os_name = Column(String(100), nullable=True, comment="操作系统")

    request_args = Column(JSON, nullable=True, comment="请求参数")
    request_body = Column(Text, nullable=True, comment="请求体")
    response_body = Column(Text, nullable=True, comment="响应内容")
    error_msg = Column(Text, nullable=True, comment="错误信息")
