from sqlalchemy import and_, select
from sqlalchemy.orm import Session, joinedload

from src.models.tenant import TenantRole
from src.repositories.base import GenericRepository


class TenantRoleRepository(GenericRepository[TenantRole, None, None]):
    def __init__(self):
        super().__init__(model=TenantRole)

    def get_by_tenant(self, tenant_id: int, session: Session) -> list[TenantRole]:
        """获取租户的所有角色"""
        query = select(TenantRole).where(
            and_(
                TenantRole.tenant_id == tenant_id,
                not TenantRole.is_deleted
            )
        )
        return list(session.execute(query).scalars().all())

    def get_with_permissions(self, id: int, tenant_id: int, session: Session) -> TenantRole | None:
        """获取角色及其权限"""
        query = select(TenantRole).where(
            and_(
                TenantRole.id == id,
                TenantRole.tenant_id == tenant_id,
                not TenantRole.is_deleted
            )
        ).options(joinedload(TenantRole.permissions))
        return session.execute(query).scalars().first()

    def is_code_exists(self, tenant_id: int, code: str, exclude_id: int = None, session: Session = None) -> bool:
        """检查角色编码是否存在"""
        query = select(TenantRole).where(
            and_(
                TenantRole.tenant_id == tenant_id,
                TenantRole.code == code,
                not TenantRole.is_deleted
            )
        )
        if exclude_id:
            query = query.where(TenantRole.id != exclude_id)
        return session.execute(query).scalars().first() is not None


tenant_role_repository = TenantRoleRepository()
