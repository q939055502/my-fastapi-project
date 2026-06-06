from sqlalchemy import BigInteger, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, TimestampMixin


class TenantMemberRole(BaseModel, TimestampMixin):
    """租户成员角色关联实体模型

    替代原有的 tenant_member_role_association 关联表，
    作为实体模型以便支持业务方法和扩展字段。
    """
    __tablename__ = "tenant_member_role"

    tenant_member_id = Column(BigInteger, ForeignKey("tenant_member.id"), nullable=False, index=True, comment="租户成员ID")
    tenant_role_id = Column(BigInteger, ForeignKey("tenant_role.id"), nullable=False, index=True, comment="租户角色ID")
    is_default = Column(Integer, default=0, nullable=False, comment="是否为默认角色：0=否，1=是")

    tenant_member = relationship("TenantMember", back_populates="member_roles")
    tenant_role = relationship("TenantRole", back_populates="role_members")
