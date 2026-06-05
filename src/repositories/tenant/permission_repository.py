from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from src.models.tenant import TenantPermission
from src.repositories.base import GenericRepository


class TenantPermissionRepository(GenericRepository[TenantPermission, None, None]):
    def __init__(self):
        super().__init__(model=TenantPermission)

    def get_by_tenant(self, tenant_id: int, session: Session) -> list[TenantPermission]:
        """获取租户的所有权限"""
        query = select(TenantPermission).where(
            and_(
                TenantPermission.tenant_id == tenant_id,
                not TenantPermission.is_deleted
            )
        )
        return list(session.execute(query).scalars().all())

    def get_by_code(self, tenant_id: int, code: str, session: Session) -> TenantPermission | None:
        """根据编码获取权限"""
        query = select(TenantPermission).where(
            and_(
                TenantPermission.tenant_id == tenant_id,
                TenantPermission.code == code,
                not TenantPermission.is_deleted
            )
        )
        return session.execute(query).scalars().first()

    def get_tree(self, tenant_id: int, session: Session) -> list[TenantPermission]:
        """获取权限树"""
        permissions = self.get_by_tenant(tenant_id, session)
        return [p for p in permissions if p.parent_id is None]

    def get_children(self, parent_id: int, session: Session) -> list[TenantPermission]:
        """获取子权限"""
        query = select(TenantPermission).where(
            and_(
                TenantPermission.parent_id == parent_id,
                not TenantPermission.is_deleted
            )
        )
        return list(session.execute(query).scalars().all())


tenant_permission_repository = TenantPermissionRepository()
