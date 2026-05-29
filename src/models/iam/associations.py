from sqlalchemy import Column, ForeignKey, Integer, Table

from src.core.storage import Base

user_role_association = Table(
    'iam_user_role',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('iam_user.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('iam_role.id'), primary_key=True),
    extend_existing=True,
)


role_resource_association = Table(
    "iam_role_resource",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("iam_role.id"), primary_key=True),
    Column("resource_id", Integer, ForeignKey("iam_resource.id"), primary_key=True),
    extend_existing=True,
)
