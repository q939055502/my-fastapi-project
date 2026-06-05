from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.iam import Role
from src.repositories.base import GenericRepository
from src.schemas.iam.role import RoleCreate, RoleUpdate


class RoleRepository(GenericRepository[Role, RoleCreate, RoleUpdate]):
    def __init__(self):
        super().__init__(model=Role)

    def is_exist(self, name: str, session: Session) -> bool:
        query = select(Role).where(Role.name == name)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first() is not None

    def is_exist_with_deleted(self, name: str, session: Session) -> bool:
        result = session.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalars().first() is not None

    def update_permissions(
        self, role: Role, permission_ids: list[int], session: Session
    ) -> None:
        role.permissions.clear()

        from src.models.iam import Permission

        for permission_id in permission_ids:
            permission_obj = session.get(Permission, permission_id)
            if permission_obj:
                role.permissions.append(permission_obj)


role_repository = RoleRepository()
