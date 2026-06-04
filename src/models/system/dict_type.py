from sqlalchemy import Column, Integer, String

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
    """字典类型模型"""
    __tablename__ = "dict_type"

    name = Column(String(50), nullable=False, comment="字典名称")
    code = Column(String(50), unique=True, nullable=False, comment="字典编码")
    tenant_id = Column(Integer, nullable=True, comment="租户ID（null=系统级）")
