from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from src.common.repository.base import GenericRepository
from src.models.platform import RolePermission
from src.modules.platform.schemas.role_permission import RolePermissionCreate, RolePermissionUpdate


class RolePermissionRepository(GenericRepository[RolePermission, RolePermissionCreate, RolePermissionUpdate]):
    def __init__(self):
        super().__init__(model=RolePermission)

    def get_by_role_id(self, role_id: int, session: Session) -> list[RolePermission]:
        """根据角色ID获取所有权限关联"""
        query = select(RolePermission).where(RolePermission.role_id == role_id)
        query = self._apply_soft_delete_filter(query)
        return session.execute(query).scalars().all()

    def delete_by_role_id(self, role_id: int, session: Session) -> None:
        """删除角色的所有权限关联"""
        session.execute(delete(RolePermission).where(RolePermission.role_id == role_id))

    def batch_create(self, role_id: int, permission_ids: list[int], created_by: int | None = None, session: Session = None) -> None:
        """批量创建角色权限关联"""
        for permission_id in permission_ids:
            role_perm = RolePermission(
                role_id=role_id,
                permission_id=permission_id,
                created_by=created_by
            )
            session.add(role_perm)

    def is_exist(self, role_id: int, permission_id: int, session: Session) -> bool:
        """检查角色权限关联是否已存在"""
        query = select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == permission_id
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first() is not None


role_permission_repository = RolePermissionRepository()
