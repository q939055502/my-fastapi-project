from sqlalchemy import Column, String

from src.models.base import (
    BaseModel,
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    SystemMixin,
    TimestampMixin,
)


class DictType(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, EnableStatusMixin, SortMixin, SystemMixin):
    """平台字典类型模型"""
    __tablename__ = "dict_type"

    name = Column(String(50), nullable=False, comment="字典名称")
    code = Column(String(50), unique=True, nullable=False, comment="字典编码")
