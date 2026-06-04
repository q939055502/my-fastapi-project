
from datetime import datetime
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from src.core.config import settings
from src.core.storage import Base


class BaseModel(Base):
    """SQLAlchemy 基础模型类"""
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, autoincrement=True)  # 主键会自动创建索引，不需要设置 index=True

    def to_dict(self, exclude_fields: list[str] | None = None) -> dict[str, Any]:
        """
        将模型对象转换为字典
        :param exclude_fields: 需要排除的字段
        :return: 模型字典
        """
        if exclude_fields is None:
            exclude_fields = []

        d = {}
        for column in self.__table__.columns:
            field_name = column.name
            if field_name not in exclude_fields:
                value = getattr(self, field_name)
                if isinstance(value, datetime):
                    value = value.strftime(settings.DATETIME_FORMAT)
                d[field_name] = value

        return d


class UUIDModel:
    """UUID 混合类"""
    uuid = Column(UUID(as_uuid=True), unique=True, index=True)


class TimestampMixin:
    """时间戳混合类"""
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SoftDeleteMixin:
    """软删除混合类"""
    is_deleted = Column(Boolean, default=False, comment="软删除标识")
    delete_time = Column(DateTime(timezone=True), nullable=True, comment="删除时间")

    def soft_delete(self):
        """执行软删除"""
        self.is_deleted = True
        self.delete_time = datetime.now()

    def restore(self):
        """恢复已删除数据"""
        self.is_deleted = False
        self.delete_time = None

    def is_deleted_status(self) -> bool:
        """判断是否已被软删除"""
        return self.is_deleted


class RemarkMixin:
    """备注描述混合类"""
    remark = Column(String(500), nullable=True, comment="备注")


class EnableStatusMixin:
    """启用/禁用状态 Mixin

    适用于需要表示启用/禁用状态的模型，使用 STATUS_ENABLED/STATUS_DISABLED 常量
    """
    status = Column(Integer, default=1, comment="状态（使用 STATUS_* 常量：1=启用，0=禁用）")


class TenantStatusMixin:
    """租户状态 Mixin

    适用于租户模型，表示租户的业务状态，使用 TENANT_STATUS_* 常量
    """
    status = Column(String(20), default="active", comment="状态（使用 TENANT_STATUS_* 常量：active/suspended/trial/expired）")


class LoginStatusMixin:
    """登录状态 Mixin

    适用于登录日志模型，表示登录结果，使用 LOGIN_STATUS_* 常量
    """
    status = Column(Integer, nullable=False, comment="登录状态（使用 LOGIN_STATUS_* 常量：1=成功，0=失败）")


class SortMixin:
    """排序字段 Mixin

    适用于需要排序的模型，提供统一的排序字段
    """
    sort = Column(Integer, default=0, comment="排序")


class SystemMixin:
    """系统标识 Mixin

    适用于需要区分系统内置和自定义的模型，系统内置数据不允许修改和删除
    """
    is_system = Column(Integer, default=0, comment="系统内置标识：0=否，1=是，系统内置数据不允许修改删除")

