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


class TenantDictData(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, EnableStatusMixin, SortMixin, SystemMixin):
    """租户字典数据模型"""
    __tablename__ = "tenant_dict_data"

    tenant_id = Column(BigInteger, ForeignKey("tenant.id"), nullable=False, index=True, comment="租户ID")
    dict_type_id = Column(BigInteger, ForeignKey("tenant_dict_type.id"), nullable=False, index=True, comment="字典类型ID")
    label = Column(String(100), nullable=False, comment="字典标签")
    value = Column(String(100), nullable=False, comment="字典值")
    css_class = Column(String(100), nullable=True, comment="样式类")

    tenant = relationship("Tenant", back_populates="dict_datas")
    dict_type = relationship("TenantDictType", backref="datas")
