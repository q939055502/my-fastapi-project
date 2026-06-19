import secrets
import string
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from src.core.storage import BaseRepository
from src.foundation.order.schemas.order import OrderCreate, OrderUpdate
from src.models.order import OrderInfo


class OrderRepository(BaseRepository[OrderInfo, OrderCreate, OrderUpdate]):
    """订单仓库"""

    def __init__(self):
        super().__init__(model=OrderInfo)

    def get_by_order_no(self, order_no: str, session: Session) -> OrderInfo | None:
        query = select(OrderInfo).where(OrderInfo.order_no == order_no)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def list_orders(
        self,
        page: int = 1,
        page_size: int = 10,
        session: Session = None,
        buyer_type: str | None = None,
        buyer_id: int | None = None,
        product_type: str | None = None,
        product_id: int | None = None,
        order_type: str | None = None,
        pay_status: str | None = None,
        order_status: str | None = None,
        order_no: str | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> tuple[int, list[OrderInfo]]:
        """分页查询订单列表"""
        filters = []

        if buyer_type:
            filters.append(OrderInfo.buyer_type == buyer_type)
        if buyer_id is not None:
            filters.append(OrderInfo.buyer_id == buyer_id)
        if product_type:
            filters.append(OrderInfo.product_type == product_type)
        if product_id is not None:
            filters.append(OrderInfo.product_id == product_id)
        if order_type:
            filters.append(OrderInfo.order_type == order_type)
        if pay_status:
            filters.append(OrderInfo.pay_status == pay_status)
        if order_status:
            filters.append(OrderInfo.order_status == order_status)
        if order_no:
            filters.append(OrderInfo.order_no.contains(order_no))
        if start_time:
            filters.append(OrderInfo.created_at >= start_time)
        if end_time:
            filters.append(OrderInfo.created_at <= end_time)

        return self.list(
            page=page,
            page_size=page_size,
            session=session,
            filters=filters,
            order_by=[desc(OrderInfo.id)],
        )

    def generate_order_no(self) -> str:
        """生成订单号:日期 + 随机数"""
        date_str = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = "".join(secrets.choice(string.digits) for _ in range(6))
        return f"ORD{date_str}{random_str}"


order_repository = OrderRepository()
