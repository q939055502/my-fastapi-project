from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, delete

from src.models.sys import Tenant, TenantPlan, User
from src.models.sys.associations import user_tenant_association


class UserTenantRepository:
    def get_user_tenants(self, user_id: int, session: Session) -> List[dict]:
        query = select(
            Tenant,
            user_tenant_association.c.is_owner,
            user_tenant_association.c.joined_at
        ).join(
            user_tenant_association,
            and_(
                user_tenant_association.c.tenant_id == Tenant.id,
                user_tenant_association.c.user_id == user_id
            )
        ).where(
            Tenant.is_deleted == False
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

    def get_tenant_members(self, tenant_id: int, session: Session) -> List[dict]:
        query = select(
            User,
            user_tenant_association.c.is_owner,
            user_tenant_association.c.joined_at
        ).join(
            user_tenant_association,
            and_(
                user_tenant_association.c.user_id == User.id,
                user_tenant_association.c.tenant_id == tenant_id
            )
        ).where(
            User.is_deleted == False
        )

        result = session.execute(query)
        rows = result.all()

        members = []
        for row in rows:
            member = {
                "user_id": row.User.id,
                "username": row.User.username,
                "email": row.User.email,
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
        query = select(user_tenant_association).where(
            and_(
                user_tenant_association.c.user_id == user_id,
                user_tenant_association.c.tenant_id == tenant_id
            )
        )
        result = session.execute(query).first()
        return result is not None

    def is_tenant_owner(self, user_id: int, tenant_id: int, session: Session) -> bool:
        query = select(user_tenant_association).where(
            and_(
                user_tenant_association.c.user_id == user_id,
                user_tenant_association.c.tenant_id == tenant_id,
                user_tenant_association.c.is_owner == True
            )
        )
        result = session.execute(query).first()
        return result is not None

    def get_tenant_by_code(self, code: str, session: Session) -> Optional[Tenant]:
        query = select(Tenant).where(
            and_(
                Tenant.code == code,
                Tenant.is_deleted == False
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
        stmt = user_tenant_association.insert().values(
            user_id=user_id,
            tenant_id=tenant_id,
            is_owner=is_owner,
            joined_at=datetime.now()
        )
        session.execute(stmt)

    def remove_user_from_tenant(self, user_id: int, tenant_id: int, session: Session) -> bool:
        if self.is_tenant_owner(user_id, tenant_id, session):
            return False

        stmt = delete(user_tenant_association).where(
            and_(
                user_tenant_association.c.user_id == user_id,
                user_tenant_association.c.tenant_id == tenant_id
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

    def get_user_tenant_relation(self, user_id: int, tenant_id: int, session: Session) -> Optional[dict]:
        query = select(
            user_tenant_association
        ).where(
            and_(
                user_tenant_association.c.user_id == user_id,
                user_tenant_association.c.tenant_id == tenant_id
            )
        )
        result = session.execute(query).first()

        if result:
            return {
                "user_id": result.user_id,
                "tenant_id": result.tenant_id,
                "is_owner": result.is_owner,
                "joined_at": result.joined_at
            }
        return None


user_tenant_repository = UserTenantRepository()
