from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.storage.generic_repository import GenericRepository
from src.models.iam import Role
from src.schemas.sys.roles import RoleCreate, RoleUpdate


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

    def update_resources(
        self, role: Role, resource_ids: list[int], session: Session
    ) -> None:
        role.resources.clear()

        from .resource_repository import resource_repository

        for resource_id in resource_ids:
            resource_obj = resource_repository.get_by_id(resource_id, session=session)
            if resource_obj:
                role.resources.append(resource_obj)


role_repository = RoleRepository()
