from sqlalchemy import Column, String, Integer, BigInteger, JSON, Text
from src.models.base import BaseModel, TimestampMixin


class AuditLog(BaseModel, TimestampMixin):
    """审计日志模型（全局操作审计）"""
    __tablename__ = "audit_log"
    __table_args__ = {'extend_existing': True}
    
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
    os = Column(String(100), nullable=True, comment="操作系统")
    
    request_args = Column(JSON, nullable=True, comment="请求参数")
    request_body = Column(Text, nullable=True, comment="请求体")
    response_body = Column(Text, nullable=True, comment="响应内容")
    error_msg = Column(Text, nullable=True, comment="错误信息")


class FileMapping(BaseModel, TimestampMixin):
    """文件映射模型（文件管理）"""
    __tablename__ = "file_mapping"
    __table_args__ = {'extend_existing': True}
    
    file_id = Column(String(255), unique=True, nullable=False, index=True, comment="文件ID")
    original_filename = Column(String(255), nullable=False, comment="原始文件名")
    file_type = Column(String(50), nullable=False, comment="文件类型")
    file_size = Column(BigInteger, nullable=True, comment="文件大小(字节)")
    file_path = Column(String(500), nullable=True, comment="本地文件路径")
    file_url = Column(String(500), nullable=True, comment="文件访问URL")
    
    storage_type = Column(String(20), default="local", comment="存储类型：local/oss/cos")
    bucket_name = Column(String(100), nullable=True, comment="存储桶名称")
    
    upload_user_id = Column(Integer, nullable=False, index=True, comment="上传用户ID")
    tenant_id = Column(Integer, nullable=True, index=True, comment="租户ID")
    
    category = Column(String(50), nullable=True, comment="文件分类：avatar/logo/attachment/image/document")
    description = Column(String(500), nullable=True, comment="文件描述")
