from sqlalchemy import select
from sqlalchemy.orm import Session
from src.common.repository.base import GenericRepository
from src.models.platform import Permission
from src.modules.platform.schemas.permission import PermissionCreate, PermissionUpdate


class PermissionRepository(GenericRepository[Permission, PermissionCreate, PermissionUpdate]):
    def __init__(self):
        super().__init__(model=Permission)

    def get_by_code(self, code: str, session: Session) -> Permission | None:
        query = select(Permission).where(Permission.code == code)
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalar_one_or_none()

    def get_by_code_with_deleted(self, code: str, session: Session) -> Permission | None:
        return session.execute(
            select(Permission).where(Permission.code == code)
        ).scalar_one_or_none()

    def get_children(self, parent_id: int, session: Session) -> list[Permission]:
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

    def exists_by_code(self, code: str, exclude_id: int | None = None, session: Session = None) -> bool:
        query = select(Permission).where(Permission.code == code)
        query = self._apply_soft_delete_filter(query)
        if exclude_id:
            query = query.where(Permission.id != exclude_id)
        return session.execute(query).first() is not None

    def exists_by_code_with_deleted(self, code: str, exclude_id: int | None = None, session: Session = None) -> bool:
        query = select(Permission).where(Permission.code == code)
        if exclude_id:
            query = query.where(Permission.id != exclude_id)
        return session.execute(query).first() is not None

    def get_permissions_by_role(self, role_id: int, session: Session) -> list[Permission]:
        from src.models.platform.associations import role_permission_association
        query = select(Permission).join(role_permission_association).where(
            role_permission_association.c.role_id == role_id
        )
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().all()

    def get_by_id(self, id: int, session: Session) -> Permission | None:
        query = select(Permission).where(Permission.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_tree(self, session: Session) -> list[Permission]:
        """获取权限树"""
        permissions = self.list(session=session)
        return [p for p in permissions if p.parent_id is None]


permission_repository = PermissionRepository()
