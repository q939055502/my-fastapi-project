
from sqlalchemy import and_, delete, insert, select

from src.core.storage import BaseRepository
from src.models.platform import RolePermission


class RolePermissionRepository(BaseRepository):
    model = RolePermission

    def get_permission_ids_by_role(self, role_id: int, session=None) -> list[int]:
        query = select(self.model.permission_id).where(
            self.model.role_id == role_id
        )
        result = self._get_session(session).execute(query)
        return [row[0] for row in result]

    def get_role_ids_by_permission(self, permission_id: int, session=None) -> list[int]:
        query = select(self.model.role_id).where(
            self.model.permission_id == permission_id
        )
        result = self._get_session(session).execute(query)
        return [row[0] for row in result]

    def batch_create(self, role_id: int, permission_ids: list[int], session=None) -> None:
        db = self._get_session(session)
        existing_ids = self.get_permission_ids_by_role(role_id, session=db)
        new_ids = [pid for pid in permission_ids if pid not in existing_ids]

        if new_ids:
            records = [
                {"role_id": role_id, "permission_id": pid}
                for pid in new_ids
            ]
            db.execute(insert(self.model), records)
            db.flush()

    def batch_remove(self, role_id: int, permission_ids: list[int], session=None) -> None:
        db = self._get_session(session)
        db.execute(
            delete(self.model).where(
                and_(
                    self.model.role_id == role_id,
                    self.model.permission_id.in_(permission_ids)
                )
            )
        )
        db.flush()

    def remove_by_role(self, role_id: int, session=None) -> None:
        db = self._get_session(session)
        db.execute(
            delete(self.model).where(self.model.role_id == role_id)
        )
        db.flush()


role_permission_repository = RolePermissionRepository(model=RolePermission)
