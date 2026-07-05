from sqlalchemy import BigInteger, Column, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import TimestampMixin


class OrgSubject(BaseModel, TimestampMixin):
    """成员-组织关联表(多对多)

    仅租户成员与组织节点挂钩,平台业务不挂组织树.
    一个成员可归属多个组织节点.
    """
    __tablename__ = "sys_org_subject"

    member_id = Column(BigInteger, nullable=False, index=True, comment="租户成员ID")
    org_id = Column(BigInteger, nullable=False, index=True, comment="组织节点ID")

    __table_args__ = (
        UniqueConstraint('member_id', 'org_id', name='uq_org_subject'),
    )
