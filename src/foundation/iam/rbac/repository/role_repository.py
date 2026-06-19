
from sqlalchemy import and_, func, select

from src.core.storage import BaseRepository
from src.models.platform import Role


class RoleRepository(BaseRepository):
    model = Role

    def get_by_code(self, code: str, session=None) -> Role | None:
        query = select(self.model).where(self.model.code == code)
        query = self._apply_soft_delete_filter(query)
        result = self._get_session(session).execute(query)
        return result.scalars().first()

    def get_by_tenant_id(self, tenant_id: int, session=None) -> list[Role]:
        query = select(self.model).where(self.model.tenant_id == tenant_id)
        query = self._apply_soft_delete_filter(query)
        result = self._get_session(session).execute(query)
        return result.scalars().all()

    def get_platform_roles(self, session=None) -> list[Role]:
        query = select(self.model).where(self.model.tenant_id.is_(None))
        query = self._apply_soft_delete_filter(query)
        result = self._get_session(session).execute(query)
        return result.scalars().all()

    def check_role_exists(self, name: str, tenant_id: int | None = None, exclude_id: int | None = None, session=None) -> bool:
        query = select(func.count(self.model.id)).where(
            and_(
                self.model.name == name,
                self.model.tenant_id == tenant_id
            )
        )
        query = self._apply_soft_delete_count_filter(query)
        if exclude_id is not None:
            query = query.where(self.model.id != exclude_id)
        result = self._get_session(session).execute(query)
        return result.scalar_one() > 0

    def list_by_ids(self, role_ids: list[int], session=None) -> list[Role]:
        """根据ID列表批量获取角色(带软删除过滤)"""
        if not role_ids:
            return []
        query = select(self.model).where(self.model.id.in_(role_ids))
        query = self._apply_soft_delete_filter(query)
        result = self._get_session(session).execute(query)
        return result.scalars().all()


role_repository = RoleRepository(model=Role)
