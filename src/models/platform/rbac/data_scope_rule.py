from sqlalchemy import BigInteger, Column, String, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import (
    RemarkMixin,
    ResourceOwnerMixin,
    SoftDeleteMixin,
    SortMixin,
    TimestampMixin,
    UUIDModel,
)


class DataScopeRule(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, UUIDModel, ResourceOwnerMixin):
    """数据范围规则表 - 定义角色对特定权限的数据访问范围

    设计理念:规则永远绑定在角色+权限上,同一角色下不同权限可配置完全不同的数据范围
    维度可无限扩展(tenant/org/creator/project/time等),通过 dimension_type 灵活定义"""
    __tablename__ = "iam_data_scope_rule"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", "dimension_type", name='uk_role_perm_dim'),
        {"comment": "数据范围规则表"},
    )

    role_id = Column(BigInteger, nullable=False, index=True, comment="规则所属角色")
    permission_id = Column(BigInteger, nullable=False, index=True, comment="规则对应的具体操作权限")
    dimension_type = Column(String(32), nullable=False, comment="维度类型:tenant/org/creator 等,可扩展")
    match_type = Column(String(32), nullable=False, comment="匹配方式:eq/all/tree/in")
    dimension_value = Column(String(255), nullable=False, comment="维度值,*全部/self当前用户/current当前组织/具体ID/多ID逗号分隔")
