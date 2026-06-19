from sqlalchemy import Column, String

from src.models.base import BaseModel
from src.models.mixins import (
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    SystemMixin,
    TimestampMixin,
    UUIDModel,
)


class DictType(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin, EnableStatusMixin, UUIDModel):
    """平台字典类型模型"""
    __tablename__ = "sys_dict_type"

    name = Column(String(50), nullable=False, comment="字典名称")
    code = Column(String(50), unique=True, nullable=False, comment="字典编码")
