from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.core.storage import BaseRepository
from src.foundation.order.schemas.order_payment import (
    OrderPaymentCreate,
    OrderPaymentResponse,
)
from src.models.order import OrderPayment


class OrderPaymentRepository(BaseRepository[OrderPayment, OrderPaymentCreate, OrderPaymentResponse]):
    """订单支付记录仓库"""

    def __init__(self):
        super().__init__(model=OrderPayment)

    def list_by_order_id(self, order_id: int, session: Session) -> list[OrderPayment]:
        """根据订单ID查询支付记录"""
        query = select(OrderPayment).where(OrderPayment.order_id == order_id)
        query = self._apply_soft_delete_filter(query)
        query = query.order_by(desc(OrderPayment.id))
        result = session.execute(query)
        return list(result.scalars().all())

    def get_by_payment_no(self, payment_no: str, session: Session) -> OrderPayment | None:
        """根据支付流水号获取记录"""
        query = select(OrderPayment).where(OrderPayment.payment_no == payment_no)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()


order_payment_repository = OrderPaymentRepository()
