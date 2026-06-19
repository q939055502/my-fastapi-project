from sqlalchemy import Boolean, Column, DateTime, Integer, String

from src.models.base import BaseModel
from src.models.mixins import RemarkMixin, SoftDeleteMixin, TimestampMixin, UUIDModel


class User(BaseModel, TimestampMixin, SoftDeleteMixin, RemarkMixin, UUIDModel):
    """用户模型 - 全局独立,不属于任何租户"""
    __tablename__ = "iam_user"

    username = Column(String(20), unique=True, nullable=False, index=True, comment="用户名称")
    alias = Column(String(30), nullable=True, index=True, comment="姓名/昵称")
    password = Column(String(128), nullable=True, comment="密码")
    avatar = Column(String(500), nullable=True, comment="头像URL")
    gender = Column(Integer, default=0, comment="性别:0未知,1男,2女")

    is_active = Column(Boolean, default=True, index=True, comment="是否激活")
    is_multi_login = Column(Boolean, default=False, comment="是否允许同一账号多端登录")

    last_login = Column(DateTime(timezone=True), nullable=True, index=True, comment="最后登录时间")
    last_login_ip = Column(String(50), nullable=True, comment="最后登录IP")
