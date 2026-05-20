
from datetime import datetime
from src.core.config import settings

from typing import List, Optional, Dict, Any
from sqlalchemy import Column, BigInteger, DateTime, Index, Integer, Sequence, Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from src.core.storage import Base


class BaseModel(Base):
    """SQLAlchemy 基础模型类"""
    __abstract__ = True

    id = Column(Integer, primary_key=True)  # 主键会自动创建索引，不需要设置 index=True

    def to_dict(self, m2m: bool = False, exclude_fields: List[str] | None = None) -> Dict[str, Any]:
        """
        将模型对象转换为字典
        :param m2m: 是否包含多对多关系
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

        if m2m:
            pass

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


class RemarkMixin:
    """备注描述混合类"""
    remark = Column(String(500), nullable=True, comment="备注")

