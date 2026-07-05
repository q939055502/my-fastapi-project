from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, Integer, String, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import (
    EnableStatusMixin,
    RemarkMixin,
    ResourceOwnerMixin,
    SoftDeleteMixin,
    SortMixin,
    TimestampMixin,
    UUIDModel,
)


class Org(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, EnableStatusMixin, UUIDModel, ResourceOwnerMixin):
    """组织节点模型"""
    __tablename__ = "sys_org"

    name = Column(String(50), nullable=False, comment="组织名称")
    code = Column(String(50), nullable=True, comment="组织编码")
    parent_id = Column(BigInteger, nullable=True, comment="父组织ID")
    level = Column(Integer, default=0, comment="组织层级")
    leader = Column(String(50), nullable=True, comment="组织负责人")
    phone = Column(String(20), nullable=True, comment="联系电话")
    email = Column(String(100), nullable=True, comment="组织邮箱")
    is_display = Column(Boolean, default=True, comment="是否显示:True=显示,False=隐藏")


class OrgClosure(BaseModel, TimestampMixin, SoftDeleteMixin, ResourceOwnerMixin):
    """组织闭包表(用于高效查询树形结构)"""
    __tablename__ = "sys_org_closure"

    __table_args__ = (
        CheckConstraint("level >= 0 AND level <= 10", name="ck_org_closure_level"),
        UniqueConstraint('tenant_id', 'ancestor', 'descendant', name='uq_org_closure_tenant_anc_desc'),
    )

    ancestor = Column(BigInteger, nullable=False, comment="祖先节点")
    descendant = Column(BigInteger, nullable=False, comment="后代节点")
    level = Column(Integer, default=0, comment="层级深度")
