from sqlalchemy import BigInteger, Column, String

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


class DictData(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin, EnableStatusMixin, UUIDModel):
    """平台字典数据模型"""
    __tablename__ = "sys_dict_data"

    dict_type_id = Column(BigInteger, index=True, comment="字典类型ID")
    label = Column(String(100), nullable=False, comment="字典标签")
    value = Column(String(100), nullable=False, comment="字典值")
    css_class = Column(String(100), nullable=True, comment="样式属性")
