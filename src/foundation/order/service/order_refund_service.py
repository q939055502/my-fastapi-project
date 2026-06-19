import secrets
import string
from datetime import datetime

from src.core.base.service_base import BaseService
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.order.enums import (
    OrderActionEnum,
    PayStatusEnum,
    RefundStatusEnum,
)
from src.foundation.order.models import OrderLog
from src.foundation.order.repository import (
    order_log_repository,
    order_refund_repository,
    order_repository,
)
from src.foundation.order.schemas.order_refund import OrderRefundCreate


class OrderRefundService(BaseService):
    """订单退款服务"""

    def __init__(self):
        super().__init__()
        self.repository = order_refund_repository
        self.order_repository = order_repository
        self.log_repository = order_log_repository

    def _generate_refund_no(self) -> str:
        date_str = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = "".join(secrets.choice(string.digits) for _ in range(6))
        return f"RF{date_str}{random_str}"

    def create_refund(
        self,
        order_uuid: str,
        refund_in: OrderRefundCreate,
        operator_id: int = None,
        operator_name: str = None,
    ) -> dict:
        """创建退款单"""
        with TransactionManager() as tm:
            order_id = self.get_id_by_uuid("order_info", order_uuid, tm.session)
            if not order_id:
                raise BusinessException(40401, detail="订单不存在")

            order_obj = self.order_repository.get(id=order_id, session=tm.session)
            if not order_obj:
                raise BusinessException(40401, detail="订单不存在")

            if order_obj.pay_status != PayStatusEnum.PAID.value:
                raise BusinessException(40000, detail="只有已支付订单可申请退款")

            refund_data = refund_in.model_dump()
            refund_data["order_id"] = order_obj.id
            refund_data["refund_no"] = self._generate_refund_no()
            refund_data["status"] = RefundStatusEnum.PENDING.value
            refund_data["operator_id"] = operator_id or refund_in.operator_id
            refund_data["operator_name"] = operator_name or refund_in.operator_name

            new_refund = self.repository.create(obj_in=refund_data, session=tm.session)

            # 记录日志
            log = OrderLog(
                order_id=order_obj.id,
                action=OrderActionEnum.REFUND.value,
                before_pay_status=order_obj.pay_status,
                after_pay_status=order_obj.pay_status,
                detail=f"申请退款,金额:{refund_in.refund_amount}分,原因:{refund_in.reason or '无'}",
                operator_id=operator_id,
                operator_name=operator_name,
            )
            tm.add(log)

            tm.commit()

            return self._transform_refund(new_refund)

    def list_refunds(self, order_uuid: str) -> list[dict]:
        """获取订单退款记录"""
        with TransactionManager() as tm:
            order_id = self.get_id_by_uuid("order_info", order_uuid, tm.session)
            if not order_id:
                raise BusinessException(40401, detail="订单不存在")

            order_obj = self.order_repository.get(id=order_id, session=tm.session)
            if not order_obj:
                raise BusinessException(40401, detail="订单不存在")

            refunds = self.repository.list_by_order_id(order_obj.id, session=tm.session)
            return [self._transform_refund(r) for r in refunds]

    def _transform_refund(self, obj) -> dict:
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            result[column.name] = value
        return result


order_refund_service = OrderRefundService()
