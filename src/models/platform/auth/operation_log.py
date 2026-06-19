from sqlalchemy import JSON, Column, Integer, String

from src.models.base import BaseModel
from src.models.mixins import RemarkMixin, SoftDeleteMixin, TimestampMixin


class OperationLog(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """业务操作日志模型"""
    __tablename__ = "sys_operation_log"

    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    tenant_id = Column(Integer, nullable=True, index=True, comment="租户ID")

    module = Column(String(50), nullable=True, comment="业务模块")
    business_type = Column(String(50), nullable=True, comment="业务类型")
    action = Column(String(50), nullable=True, comment="操作动作")

    target_type = Column(String(50), nullable=True, comment="操作对象类型")
    target_id = Column(String(100), nullable=True, comment="操作对象ID")
    target_name = Column(String(200), nullable=True, comment="操作对象名称")

    old_value = Column(JSON, nullable=True, comment="修改前的值")
    new_value = Column(JSON, nullable=True, comment="修改后的值")

    request_method = Column(String(10), nullable=True, comment="请求方法")
    request_url = Column(String(500), nullable=True, comment="请求URL")
    request_params = Column(JSON, nullable=True, comment="请求参数")

    response_status = Column(Integer, nullable=True, comment="响应状态")
    response_time = Column(Integer, nullable=True, comment="响应时间(ms)")

    ip = Column(String(50), nullable=True, comment="IP地址")
    location = Column(String(200), nullable=True, comment="操作地点")
    user_agent = Column(String(500), nullable=True, comment="User Agent")
