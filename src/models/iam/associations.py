from sqlalchemy import BigInteger, Column, ForeignKey, Table

from src.core.storage import Base

user_role_association = Table(
    'iam_user_role',
    Base.metadata,
    Column('user_id', BigInteger, ForeignKey('iam_user.id'), primary_key=True),
    Column('role_id', BigInteger, ForeignKey('iam_role.id'), primary_key=True),
    extend_existing=True,
)


role_permission_association = Table(
    'iam_role_permission',
    Base.metadata,
    Column('role_id', BigInteger, ForeignKey('iam_role.id'), primary_key=True),
    Column('permission_id', BigInteger, ForeignKey('iam_permission.id'), primary_key=True),
    extend_existing=True,
)
