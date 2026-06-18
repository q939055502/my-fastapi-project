from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from src.core.storage import BaseRepository
from src.foundation.order.models import OrderLog


class OrderLogRepository(BaseRepository):
    """订单操作日志仓库"""

    def __init__(self):
        super().__init__(model=OrderLog)

    def list_by_order_id(self, order_id: int, session: Session) -> list[OrderLog]:
        """根据订单ID查询操作日志"""
        query = select(OrderLog).where(OrderLog.order_id == order_id)
        query = self._apply_soft_delete_filter(query)
        query = query.order_by(desc(OrderLog.id))
        result = session.execute(query)
        return list(result.scalars().all())


order_log_repository = OrderLogRepository()