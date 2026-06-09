from sqlalchemy import BigInteger, Column, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from src.models.base import (
    BaseModel,
    RemarkMixin,
    SoftDeleteMixin,
    SortMixin,
    SystemMixin,
    TimestampMixin,
)


class Permission(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, SortMixin, SystemMixin):
    """平台权限表"""
    __tablename__ = "iam_permission"

    name = Column(String(50), nullable=False, comment="权限名称")
    resource = Column(String(50), nullable=False, index=True, comment="资源标识，如user、role等")
    action = Column(String(30), nullable=False, index=True, comment="操作类型，如create、read、update、delete等")
    scope = Column(String(20), nullable=False, default="self", index=True, comment="数据范围：self/own/dept/dept_all/all")
    type = Column(String(20), nullable=False, index=True, comment="权限类型：menu/button/api")
    applicable_scope = Column(String(20), nullable=False, default="tenant", index=True, comment="适用范围：platform(平台专用)/tenant(租户可用)")
    parent_id = Column(BigInteger, ForeignKey("iam_permission.id"), nullable=True, index=True, comment="父级权限ID")
    
    __table_args__ = (
        UniqueConstraint('resource', 'action', 'scope', name='uq_permission_resource_action_scope'),
    )

    parent = relationship("Permission", remote_side="Permission.id")
    children = relationship("Permission", back_populates="parent")
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")
    
    @property
    def permission_code(self) -> str:
        """生成权限编码：{resource}:{action}:{scope}"""
        return f"{self.resource}:{self.action}:{self.scope}"
