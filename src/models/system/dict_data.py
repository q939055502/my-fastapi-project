from sqlalchemy import BigInteger, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from src.models.base import (
    BaseModel,
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    SystemMixin,
    TimestampMixin,
)


class DictData(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, EnableStatusMixin, SortMixin, SystemMixin):
    """字典数据模型"""
    __tablename__ = "dict_data"

    dict_type_id = Column(BigInteger, ForeignKey("dict_type.id"), nullable=False, index=True, comment="字典类型ID")
    label = Column(String(100), nullable=False, comment="字典标签")
    value = Column(String(100), nullable=False, comment="字典值")
    css_class = Column(String(100), nullable=True, comment="样式类")
    list_class = Column(String(100), nullable=True, comment="列表样式")
    tenant_id = Column(BigInteger, nullable=True, index=True, comment="租户ID（null=系统级）")

    dict_type = relationship("DictType", backref="datas")
