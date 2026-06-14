from datetime import datetime

from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session
from src.models.platform import User
from src.models.tenant import Tenant, TenantMember
from src.foundation.tenant.repository.base import TenantRepositoryBase


class TenantMemberRepository(TenantRepositoryBase[TenantMember, None, None]):
    def __init__(self):
        super().__init__(model=TenantMember)

    def get_user_tenants(self, user_id: int, session: Session) -> list[dict]:
        """获取用户加入的所有租户（跨租户查询，不限制当前上下文租户）"""
        query = select(
            Tenant,
            TenantMember.is_owner,
            TenantMember.joined_at
        ).join(
            TenantMember,
            and_(
                TenantMember.tenant_id == Tenant.id,
                TenantMember.user_id == user_id
            )
        ).where(
            Tenant.delete_time.is_(None),
            TenantMember.delete_time.is_(None)
        )

        result = session.execute(query)
        rows = result.all()

        return [
            {
                "tenant_id": row.Tenant.id,
                "tenant_name": row.Tenant.name,
                "tenant_code": row.Tenant.code,
                "is_owner": row.is_owner,
                "joined_at": row.joined_at
            }
            for row in rows
        ]

    def get_tenant_members(self, tenant_id: int, session: Session) -> list[dict]:
        """获取指定租户的成员列表"""
        query = select(
            User,
            TenantMember.is_owner,
            TenantMember.joined_at
        ).join(
            TenantMember,
            and_(
                TenantMember.user_id == User.id,
                TenantMember.tenant_id == tenant_id
            )
        ).where(
            User.delete_time.is_(None),
            TenantMember.delete_time.is_(None)
        )

        result = session.execute(query)
        rows = result.all()

        members = []
        for row in rows:
            email = None
            if hasattr(row.User, "account_binds"):
                for bind in row.User.account_binds:
                    if bind.bind_type == 1 and bind.status == "verified":
                        email = bind.identifier
                        break
            member = {
                "user_id": row.User.id,
                "username": row.User.username,
                "email": email,
                "is_owner": row.is_owner,
                "joined_at": row.joined_at,
                "roles": [
                    {
                        "id": role.id,
                        "name": role.name
                    }
                    for role in row.User.roles
                ]
            }
            members.append(member)

        return members

    def is_user_in_tenant(self, user_id: int, tenant_id: int, session: Session) -> bool:
        """检查用户是否在指定租户中"""
        query = select(TenantMember).where(
            and_(
                TenantMember.user_id == user_id,
                TenantMember.tenant_id == tenant_id,
                TenantMember.delete_time.is_(None)
            )
        )
        result = session.execute(query).first()
        return result is not None

    def is_tenant_owner(self, user_id: int, tenant_id: int, session: Session) -> bool:
        """检查用户是否为租户所有者"""
        query = select(TenantMember).where(
            and_(
                TenantMember.user_id == user_id,
                TenantMember.tenant_id == tenant_id,
                TenantMember.is_owner,
                TenantMember.delete_time.is_(None)
            )
        )
        result = session.execute(query).first()
        return result is not None

    def get_tenant_by_code(self, code: str, session: Session) -> Tenant | None:
        """根据租户编码获取租户信息"""
        query = select(Tenant).where(
            and_(
                Tenant.code == code,
                Tenant.delete_time.is_(None)
            )
        )
        result = session.execute(query).scalars().first()
        return result

    def add_user_to_tenant(
        self,
        user_id: int,
        tenant_id: int,
        is_owner: bool = False,
        session: Session = None
    ) -> None:
        tenant_member = TenantMember(
            user_id=user_id,
            tenant_id=tenant_id,
            is_owner=is_owner,
            joined_at=datetime.now()
        )
        session.add(tenant_member)

    def remove_user_from_tenant(self, user_id: int, tenant_id: int, session: Session) -> bool:
        if self.is_tenant_owner(user_id, tenant_id, session):
            return False

        stmt = delete(TenantMember).where(
            and_(
                TenantMember.user_id == user_id,
                TenantMember.tenant_id == tenant_id
            )
        )
        session.execute(stmt)
        return True

    def create_tenant_with_owner(self, tenant_data: dict, owner_user_id: int, session: Session) -> Tenant:
        tenant = Tenant(**tenant_data)
        session.add(tenant)
        session.flush()

        self.add_user_to_tenant(
            user_id=owner_user_id,
            tenant_id=tenant.id,
            is_owner=True,
            session=session
        )

        return tenant

    def get_user_tenant_relation(self, user_id: int, tenant_id: int, session: Session) -> dict | None:
        """获取用户与租户的关系信息"""
        query = select(
            TenantMember
        ).where(
            and_(
                TenantMember.user_id == user_id,
                TenantMember.tenant_id == tenant_id,
                TenantMember.delete_time.is_(None)
            )
        )
        result = session.execute(query).first()

        if result:
            return {
                "user_id": result.TenantMember.user_id,
                "tenant_id": result.TenantMember.tenant_id,
                "is_owner": result.TenantMember.is_owner,
                "joined_at": result.TenantMember.joined_at
            }
        return None


tenant_member_repository = TenantMemberRepository()
