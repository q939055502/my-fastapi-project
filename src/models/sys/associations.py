from src.core.storage import Base
from sqlalchemy import Column, BigInteger, ForeignKey, Table, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime


user_role_association = Table(
    'user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('role.id'), primary_key=True),
    extend_existing=True,
)


role_resource_association = Table(
    "role_resource",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("role.id"), primary_key=True),
    Column("resource_id", Integer, ForeignKey("resource.id"), primary_key=True),
    extend_existing=True,
)


user_tenant_association = Table(
    "user_tenant",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("tenant_id", Integer, ForeignKey("tenant.id"), primary_key=True),
    Column("is_owner", Boolean, default=False, nullable=False, comment="是否为户主创建人"),
    Column("joined_at", DateTime(timezone=True), default=datetime.now, nullable=False, comment="加入时间"),
    extend_existing=True,
)
