
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    and_,
)
from sqlalchemy.orm import relationship

from src.models.base import BaseModel, RemarkMixin, SoftDeleteMixin, TimestampMixin, UUIDModel


class User(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, UUIDModel):
    """用户模型 - 全局独立，不属于任何租户"""
    __tablename__ = "iam_user"

    username = Column(String(20), unique=True, nullable=False, index=True, comment="用户名称")
    alias = Column(String(30), nullable=True, index=True, comment="姓名/昵称")
    password = Column(String(128), nullable=True, comment="密码")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    gender = Column(Integer, default=0, comment="性别：0=未知，1=男，2=女")

    is_active = Column(Boolean, default=True, index=True, comment="是否激活")
    is_multi_login = Column(Boolean, default=False, comment="是否允许同一账号多端登录")

    last_login = Column(DateTime(timezone=True), nullable=True, index=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")

    dept_id = Column(BigInteger, ForeignKey("iam_dept.id"), nullable=True, index=True, comment="部门ID")
    dept = relationship("Dept", back_populates="users", foreign_keys=[dept_id])
    role_subjects = relationship("RoleSubject", viewonly=True, primaryjoin="and_(RoleSubject.subject_type==0, foreign(RoleSubject.subject_id)==User.id)")
    tenant_memberships = relationship("TenantMember", back_populates="user", cascade="all, delete-orphan")
    account_binds = relationship("AccountBind", back_populates="user", cascade="all, delete-orphan")

    def is_active_user(self) -> bool:
        """判断用户是否处于激活状态"""
        return self.is_active and self.delete_time is None

    def has_role(self, role_name: str) -> bool:
        """判断用户是否拥有指定角色"""
        for role_subject in self.role_subjects:
            if role_subject.role and role_subject.role.name == role_name:
                return True
        return False

