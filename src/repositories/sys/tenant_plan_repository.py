from sqlalchemy.orm import Session
from sqlalchemy import select

from src.core.storage.generic_repository import GenericRepository
from src.models.sys.tenant import TenantPlan
from src.schemas.sys.tenant_plan import TenantPlanCreate, TenantPlanUpdate


class TenantPlanRepository(GenericRepository[TenantPlan, TenantPlanCreate, TenantPlanUpdate]):
    def __init__(self):
        super().__init__(model=TenantPlan)

    def is_exist(self, code: str, session: Session) -> bool:
        """检查套餐编码是否存在（过滤软删除）"""
        query = select(TenantPlan).where(TenantPlan.code == code)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first() is not None


tenant_plan_repository = TenantPlanRepository()
