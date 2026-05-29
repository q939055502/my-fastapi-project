
from datetime import datetime
from typing import Any

from sqlalchemy import (
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

    id = Column(Integer, primary_key=True)  # 主键会自动创建索引，不需要设置 index=True

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

