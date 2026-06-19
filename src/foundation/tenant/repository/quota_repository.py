from sqlalchemy import select
from sqlalchemy.orm import Session
from src.foundation.tenant.repository.base import TenantRepositoryBase
from src.models.tenant import Quota


class QuotaRepository(TenantRepositoryBase[Quota, None, None]):
    """租户配额仓库"""

    def __init__(self):
        super().__init__(model=Quota)

    def get_by_tenant_id(self, tenant_id: int, session: Session) -> Quota | None:
        """根据租户ID获取配额信息"""
        query = select(Quota).where(Quota.tenant_id == tenant_id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()


quota_repository = QuotaRepository()
