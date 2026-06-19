from sqlalchemy import BigInteger, Column, String

from src.models.base import BaseModel
from src.models.mixins import (
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    TimestampMixin,
)


class DictData(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, EnableStatusMixin):
    """租户字典数据模型"""
    __tablename__ = "platform_dict_data"

    tenant_id = Column(BigInteger, nullable=False, index=True, comment="租户ID")
    dict_type_id = Column(BigInteger, nullable=False, index=True, comment="字典类型ID")
    label = Column(String(100), nullable=False, comment="字典标签")
    value = Column(String(100), nullable=False, comment="字典值")
    css_class = Column(String(100), nullable=True, comment="样式属性")
