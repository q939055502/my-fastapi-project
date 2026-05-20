from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin
from .associations import user_role_association, user_tenant_association


class User(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin):
    """用户模型 - 全局独立，不属于任何租户"""
    __tablename__ = "user"
    __table_args__ = {'extend_existing': True}
    
    username = Column(String(20), unique=True, nullable=False, index=True, comment="用户名称")
    alias = Column(String(30), nullable=True, index=True, comment="姓名/昵称")
    email = Column(String(255), unique=True, nullable=False, index=True, comment="邮箱")
    phone = Column(String(20), unique=True, nullable=True, index=True, comment="手机号")
    password = Column(String(128), nullable=True, comment="密码")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    gender = Column(Integer, default=0, comment="性别：0=未知，1=男，2=女")
    
    is_active = Column(Boolean, default=True, index=True, comment="是否激活")
    is_multi_login = Column(Boolean, default=False, comment="是否允许同一账号多端登录")
    
    last_login = Column(DateTime(timezone=True), nullable=True, index=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
    
    position = Column(String(50), nullable=True, comment="职位")
    
    can_create_sub_account = Column(Boolean, default=False, comment="是否能创建子账号")
    
    dept_id = Column(Integer, ForeignKey("dept.id"), nullable=True, index=True, comment="部门ID")
    dept = relationship("Dept", back_populates="users", foreign_keys=[dept_id])

    roles = relationship("Role", secondary=user_role_association, back_populates="users")
    tenants = relationship("Tenant", secondary=user_tenant_association, back_populates="members")
