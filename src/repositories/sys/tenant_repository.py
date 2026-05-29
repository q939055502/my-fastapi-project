from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.storage.generic_repository import GenericRepository
from src.models.tenant import Tenant
from src.schemas.sys.tenant import TenantCreate, TenantUpdate


class TenantRepository(GenericRepository[Tenant, TenantCreate, TenantUpdate]):
    def __init__(self):
        super().__init__(model=Tenant)

    def is_exist(self, code: str, session: Session) -> bool:
        """检查租户编码是否存在（过滤软删除）"""
        query = select(Tenant).where(Tenant.code == code)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first() is not None


tenant_repository = TenantRepository()
