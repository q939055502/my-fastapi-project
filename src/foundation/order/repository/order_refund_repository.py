from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from src.core.storage import BaseRepository
from src.foundation.order.models import OrderRefund
from src.foundation.order.schemas.order_refund import OrderRefundCreate, OrderRefundResponse


class OrderRefundRepository(BaseRepository[OrderRefund, OrderRefundCreate, OrderRefundResponse]):
    """订单退款记录仓库"""

    def __init__(self):
        super().__init__(model=OrderRefund)

    def list_by_order_id(self, order_id: int, session: Session) -> list[OrderRefund]:
        """根据订单ID查询退款记录"""
        query = select(OrderRefund).where(OrderRefund.order_id == order_id)
        query = self._apply_soft_delete_filter(query)
        query = query.order_by(desc(OrderRefund.id))
        result = session.execute(query)
        return list(result.scalars().all())

    def get_by_refund_no(self, refund_no: str, session: Session) -> OrderRefund | None:
        """根据退款单号获取记录"""
        query = select(OrderRefund).where(OrderRefund.refund_no == refund_no)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()


order_refund_repository = OrderRefundRepository()