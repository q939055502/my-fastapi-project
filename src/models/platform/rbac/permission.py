from sqlalchemy import BigInteger, Column, String, UniqueConstraint

from src.models.base import BaseModel
from src.models.mixins import (
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    SystemMixin,
    TimestampMixin,
    UUIDModel,
)


class Permission(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin, UUIDModel):
    """平台权限表"""
    __tablename__ = "iam_permission"

    name = Column(String(50), nullable=False, comment="权限名称")
    resource = Column(String(50), nullable=False, index=True, comment="资源标识,如user, role")
    action = Column(String(30), nullable=False, index=True, comment="操作类型,如create, read, update, delete")
    type = Column(String(20), nullable=False, index=True, comment="权限类型:menu/button/api")
    applicable_scope = Column(String(20), nullable=False, default="tenant", index=True, comment="适用范围:platform(平台专用)/tenant(租户可用)")
    parent_id = Column(BigInteger, nullable=True, index=True, comment="父级权限ID")

    __table_args__ = (
        UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
    )

    @property
    def permission_code(self) -> str:
        """生成权限编码:{resource}:{action}"""
        return f"{self.resource}:{self.action}"
