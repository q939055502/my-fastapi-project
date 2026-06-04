from sqlalchemy import BigInteger, Column, ForeignKey, Table

from src.core.storage import Base

tenant_member_role_association = Table(
    "tenant_member_role",
    Base.metadata,
    Column("tenant_member_id", BigInteger, ForeignKey("tenant_member.id"), primary_key=True),
    Column("tenant_role_id", BigInteger, ForeignKey("tenant_role.id"), primary_key=True),
    extend_existing=True,
)

tenant_role_permission_association = Table(
    "tenant_role_permission",
    Base.metadata,
    Column("tenant_role_id", BigInteger, ForeignKey("tenant_role.id"), primary_key=True),
    Column("tenant_permission_id", BigInteger, ForeignKey("tenant_permission.id"), primary_key=True),
    extend_existing=True,
)
