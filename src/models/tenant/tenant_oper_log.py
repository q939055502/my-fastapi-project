from sqlalchemy import JSON, BigInteger, Column, Integer, String, Text

from src.models.base import BaseModel, TimestampMixin


class TenantOperLog(BaseModel, TimestampMixin):
    """租户操作日志模型 - 记录租户内部成员操作"""

    __tablename__ = "tenant_oper_log"

    tenant_id = Column(BigInteger, nullable=False, index=True, comment="租户ID")
    member_id = Column(BigInteger, nullable=False, index=True, comment="租户成员ID")
    username = Column(String(64), nullable=False, index=True, comment="用户名")

    perm_code = Column(String(100), nullable=True, index=True, comment="权限编码（资源:操作）")
    module = Column(String(50), nullable=True, index=True, comment="功能模块")
    summary = Column(String(128), nullable=True, index=True, comment="操作描述")
    business_type = Column(String(50), nullable=True, comment="业务类型")

    target_type = Column(String(50), nullable=True, comment="操作对象类型")
    target_id = Column(String(100), nullable=True, index=True, comment="操作对象ID")
    target_name = Column(String(200), nullable=True, comment="操作对象名称")

    method = Column(String(10), nullable=True, index=True, comment="请求方法")
    path = Column(String(255), nullable=True, index=True, comment="请求路径")
    request_args = Column(JSON, nullable=True, comment="请求参数")
    request_body = Column(Text, nullable=True, comment="请求体")

    status = Column(Integer, default=-1, index=True, comment="状态码")
    response_time = Column(Integer, default=0, comment="响应时间(单位ms)")
    response_body = Column(Text, nullable=True, comment="响应内容")
    error_msg = Column(Text, nullable=True, comment="错误信息")

    ip = Column(String(50), nullable=True, index=True, comment="IP地址")
    location = Column(String(200), nullable=True, comment="操作地点")
    device = Column(String(100), nullable=True, comment="设备信息")
    browser = Column(String(100), nullable=True, comment="浏览器")
    os_name = Column(String(100), nullable=True, comment="操作系统")
    user_agent = Column(String(500), nullable=True, comment="User Agent")
