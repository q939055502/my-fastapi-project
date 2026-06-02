from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.models.base import (
    BaseModel,
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class DictData(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, EnableStatusMixin):
    """字典数据模型"""
    __tablename__ = "dict_data"

    dict_type_id = Column(BigInteger, ForeignKey("dict_type.id"), nullable=False, index=True, comment="字典类型ID")
    label = Column(String(100), nullable=False, comment="字典标签")
    value = Column(String(100), nullable=False, comment="字典值")
    sort = Column(Integer, default=0, comment="排序")
    css_class = Column(String(100), nullable=True, comment="样式类")
    list_class = Column(String(100), nullable=True, comment="列表样式")
    tenant_id = Column(BigInteger, nullable=True, index=True, comment="租户ID（null=系统级）")
    is_system = Column(Boolean, default=False, nullable=False, comment="系统内置数据，创建后不可修改")

    dict_type = relationship("DictType", backref="datas")
