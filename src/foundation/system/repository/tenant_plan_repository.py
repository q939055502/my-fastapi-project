from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.storage import BaseRepository
from src.foundation.system.schemas.tenant_plan import TenantPlanCreate, TenantPlanUpdate
from src.models.platform import TenantPlan


class TenantPlanRepository(BaseRepository[TenantPlan, TenantPlanCreate, TenantPlanUpdate]):
    def __init__(self):
        super().__init__(model=TenantPlan)

    def is_exist(self, code: str, session: Session) -> bool:
        """检查套餐编码是否存在(过滤软删除)"""
        query = select(TenantPlan).where(TenantPlan.code == code)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first() is not None


tenant_plan_repository = TenantPlanRepository()
