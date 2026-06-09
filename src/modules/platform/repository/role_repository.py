from sqlalchemy import select
from sqlalchemy.orm import Session
from src.common.repository.base import GenericRepository
from src.models.platform import Role
from src.modules.platform.repository.role_permission_repository import role_permission_repository
from src.modules.platform.schemas.role import RoleCreate, RoleUpdate


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
        self, role: Role, permission_ids: list[int], session: Session, created_by: int | None = None
    ) -> None:
        # 删除旧的关联
        role_permission_repository.delete_by_role_id(role.id, session)

        # 添加新的关联
        role_permission_repository.batch_create(role.id, permission_ids, created_by, session)


role_repository = RoleRepository()
