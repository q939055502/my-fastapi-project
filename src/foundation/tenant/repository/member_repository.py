from datetime import datetime

from sqlalchemy import and_, delete, select
from sqlalchemy.orm import Session
from src.foundation.tenant.repository.base import TenantRepositoryBase
from src.models.platform import AccountBind, User
from src.models.tenant import Member, Tenant


class MemberRepository(TenantRepositoryBase[Member, None, None]):
    def __init__(self):
        super().__init__(model=Member)

    def get_user_tenants(self, user_id: int, session: Session) -> list[dict]:
        """获取用户加入的所有租户(跨租户查询,不限制当前上下文租户)"""
        query = select(
            Tenant,
            Member.is_owner,
            Member.joined_at
        ).join(
            Member,
            and_(
                Member.tenant_id == Tenant.id,
                Member.user_id == user_id
            )
        ).where(
            Tenant.delete_time.is_(None),
            Member.delete_time.is_(None)
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
            Member.is_owner,
            Member.joined_at
        ).join(
            Member,
            and_(
                Member.user_id == User.id,
                Member.tenant_id == tenant_id
            )
        ).where(
            User.delete_time.is_(None),
            Member.delete_time.is_(None)
        )

        result = session.execute(query)
        rows = result.all()

        members = []
        for row in rows:
            # 查询用户的邮箱绑定
            email_query = select(AccountBind).where(
                AccountBind.user_id == row.User.id,
                AccountBind.bind_type == 1,
                AccountBind.status == "verified",
                AccountBind.delete_time.is_(None)
            )
            email_result = session.execute(email_query).scalars().first()
            email = email_result.identifier if email_result else None

            member = {
                "user_id": row.User.id,
                "username": row.User.username,
                "email": email,
                "is_owner": row.is_owner,
                "joined_at": row.joined_at,
            }
            members.append(member)

        return members

    def is_user_in_tenant(self, user_id: int, tenant_id: int, session: Session) -> bool:
        """检查用户是否在指定租户中"""
        query = select(Member).where(
            and_(
                Member.user_id == user_id,
                Member.tenant_id == tenant_id
            )
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query).first()
        return result is not None

    def is_tenant_owner(self, user_id: int, tenant_id: int, session: Session) -> bool:
        """检查用户是否为租户所有者"""
        query = select(Member).where(
            and_(
                Member.user_id == user_id,
                Member.tenant_id == tenant_id,
                Member.is_owner
            )
        )
        query = self._apply_soft_delete_filter(query)
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
        tenant_member = Member(
            user_id=user_id,
            tenant_id=tenant_id,
            is_owner=is_owner,
            joined_at=datetime.now()
        )
        session.add(tenant_member)

    def remove_user_from_tenant(self, user_id: int, tenant_id: int, session: Session) -> bool:
        if self.is_tenant_owner(user_id, tenant_id, session):
            return False

        stmt = delete(Member).where(
            and_(
                Member.user_id == user_id,
                Member.tenant_id == tenant_id
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
        query = select(Member).where(
            and_(
                Member.user_id == user_id,
                Member.tenant_id == tenant_id
            )
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query).first()

        if result:
            return {
                "user_id": result.Member.user_id,
                "tenant_id": result.Member.tenant_id,
                "is_owner": result.Member.is_owner,
                "joined_at": result.Member.joined_at
            }
        return None


tenant_member_repository = MemberRepository()
