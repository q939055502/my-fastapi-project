from sqlalchemy import BigInteger, Column, String, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import (
    EnableStatusMixin,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    TimestampMixin,
)


class DictType(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, EnableStatusMixin):
    """租户字典类型模型"""
    __tablename__ = "platform_dict_type"
    __table_args__ = (UniqueConstraint("tenant_id", "code", name="uq_platform_dict_type_code"),)

    tenant_id = Column(BigInteger, nullable=False, index=True, comment="租户ID")
    name = Column(String(50), nullable=False, comment="字典名称")
    code = Column(String(50), nullable=False, index=True, comment="字典编码")
