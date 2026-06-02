from sqlalchemy import Boolean, Column, Integer, String

from src.models.base import (
    BaseModel,
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    TimestampMixin,
)


class DictType(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, EnableStatusMixin):
    """字典类型模型"""
    __tablename__ = "dict_type"

    name = Column(String(50), nullable=False, comment="字典名称")
    code = Column(String(50), unique=True, nullable=False, comment="字典编码")
    sort = Column(Integer, default=0, comment="排序")
    tenant_id = Column(Integer, nullable=True, comment="租户ID（null=系统级）")
    is_system = Column(Boolean, default=False, nullable=False, comment="系统内置字典，创建后不可修改")
