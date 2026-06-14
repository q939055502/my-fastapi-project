from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.common.repository.base import GenericRepository
from src.models.platform import Permission, RolePermission
from src.foundation.platform.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionRepository(GenericRepository[Permission, PermissionCreate, PermissionUpdate]):
    def __init__(self):
        super().__init__(model=Permission)

    def get_by_permission_code(self, permission_code: str, session: Session = None) -> Permission | None:
        resource, action, scope = permission_code.split(":")
        
        query = select(Permission).where(
            Permission.resource == resource,
            Permission.action == action,
            Permission.scope == scope
        )
        
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalar_one_or_none()

    def get_children(self, parent_uuid: UUID, session: Session) -> list[Permission]:
        parent_id = None
        if parent_uuid:
            parent = self.get_by_uuid(parent_uuid, session)
            parent_id = parent.id if parent else None
            
        query = select(Permission).where(
            Permission.parent_id == parent_id
        )
        query = self._apply_soft_delete_filter(query)
        return session.execute(
            query.order_by(Permission.sort.asc())
        ).scalars().all()

    def get_children_with_deleted(self, parent_id: int, session: Session) -> list[Permission]:
        return session.execute(
            select(Permission).where(
                Permission.parent_id == parent_id
            ).order_by(Permission.sort.asc())
        ).scalars().all()

    def exists_by_permission_code(self, permission_code: str, exclude_id: int | None = None, session: Session = None) -> bool:
        resource, action, scope = permission_code.split(":")
        
        query = select(Permission).where(
            Permission.resource == resource,
            Permission.action == action,
            Permission.scope == scope
        )
        if exclude_id:
            query = query.where(Permission.id != exclude_id)
        
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).first() is not None

    def get_permissions_by_role(self, role_id: int, session: Session) -> list[Permission]:
        query = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().all()

    def get_by_id(self, id: int, session: Session) -> Permission | None:
        query = select(Permission).where(Permission.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_tree(self, session: Session) -> list[Permission]:
        permissions = self.list(session=session)
        return [p for p in permissions if p.parent_id is None]

    def get_platform_permissions(self, session: Session) -> list[Permission]:
        query = select(Permission).where(Permission.applicable_scope == "platform")
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().all()

    def get_tenant_permissions(self, session: Session) -> list[Permission]:
        query = select(Permission).where(Permission.applicable_scope == "tenant")
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().all()


permission_repository = PermissionRepository()