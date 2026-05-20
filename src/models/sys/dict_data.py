from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.models.base import BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin


class DictData(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """字典数据模型"""
    __tablename__ = "dict_data"
    __table_args__ = {'extend_existing': True}
    
    dict_type_id = Column(Integer, ForeignKey("dict_type.id"), nullable=False, index=True, comment="字典类型ID")
    label = Column(String(100), nullable=False, comment="字典标签")
    value = Column(String(100), nullable=False, comment="字典值")
    sort = Column(Integer, default=0, comment="排序")
    status = Column(Integer, default=1, comment="状态（1=启用，0=禁用）")
    css_class = Column(String(100), nullable=True, comment="样式类")
    list_class = Column(String(100), nullable=True, comment="列表样式")
    tenant_id = Column(Integer, nullable=True, index=True, comment="租户ID（null=系统级）")
    is_system = Column(Boolean, default=False, nullable=False, comment="系统内置数据，创建后不可修改")
    
    dict_type = relationship("DictType", backref="datas")
