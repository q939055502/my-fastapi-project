from typing import List, Optional

from sqlalchemy import and_, func, select

from src.core.storage import BaseRepository
from src.models.platform import Permission


class PermissionRepository(BaseRepository):
    model = Permission

    def get_permissions_by_role(self, role_id: int, session=None) -> List[Permission]:
        query = select(self.model).join(
            self.model.roles
        ).where(self.model.role_id == role_id)
        query = self._apply_soft_delete_filter(query)
        result = self._get_session(session).execute(query)
        return result.scalars().all()

    def get_by_resource_and_action(self, resource: str, action: str, session=None) -> Optional[Permission]:
        query = select(self.model).where(
            and_(
                self.model.resource == resource,
                self.model.action == action
            )
        )
        query = self._apply_soft_delete_filter(query)
        result = self._get_session(session).execute(query)
        return result.scalars().first()

    def get_by_resource(self, resource: str, session=None) -> List[Permission]:
        query = select(self.model).where(self.model.resource == resource)
        query = self._apply_soft_delete_filter(query)
        result = self._get_session(session).execute(query)
        return result.scalars().all()

    def list_by_scope(self, scope: str, session=None) -> List[Permission]:
        query = select(self.model).where(self.model.scope == scope)
        query = self._apply_soft_delete_filter(query)
        result = self._get_session(session).execute(query)
        return result.scalars().all()


permission_repository = PermissionRepository(model=Permission)
