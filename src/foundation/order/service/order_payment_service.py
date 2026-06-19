from datetime import datetime

from src.core.base.service_base import BaseService
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.order.enums import OrderActionEnum, PayStatusEnum
from src.foundation.order.repository import (
    order_log_repository,
    order_payment_repository,
    order_repository,
)
from src.foundation.order.schemas.order_payment import OrderPaymentCreate


class OrderPaymentService(BaseService):
    """订单支付服务"""

    def __init__(self):
        super().__init__()
        self.repository = order_payment_repository
        self.order_repository = order_repository
        self.log_repository = order_log_repository

    def create_payment(
        self,
        order_uuid: str,
        payment_in: OrderPaymentCreate,
        operator_id: int = None,
        operator_name: str = None,
    ) -> dict:
        """创建支付记录"""
        with TransactionManager() as tm:
            order_id = self.get_id_by_uuid("order_info", order_uuid, tm.session)
            if not order_id:
                raise BusinessException(40401, detail="订单不存在")

            order_obj = self.order_repository.get(id=order_id, session=tm.session)
            if not order_obj:
                raise BusinessException(40401, detail="订单不存在")

            payment_data = payment_in.model_dump()
            payment_data["order_id"] = order_obj.id
            payment_data["status"] = PayStatusEnum.PAID.value
            payment_data["paid_at"] = datetime.now()

            new_payment = self.repository.create(obj_in=payment_data, session=tm.session)

            # 更新订单状态
            before_pay = order_obj.pay_status
            order_obj.pay_status = PayStatusEnum.PAID.value
            if order_obj.order_status == "pending":
                order_obj.order_status = "processing"

            # 记录日志
            from src.foundation.order.models import OrderLog

            log = OrderLog(
                order_id=order_obj.id,
                action=OrderActionEnum.PAY.value,
                before_pay_status=before_pay,
                after_pay_status=order_obj.pay_status,
                before_order_status=None,
                after_order_status=order_obj.order_status,
                operator_id=operator_id,
                operator_name=operator_name,
                detail=f"支付成功,金额:{payment_in.amount}分,方式:{payment_in.payment_method}",
            )
            tm.add(log)

            tm.commit()

            return self._transform_payment(new_payment)

    def list_payments(self, order_uuid: str) -> list[dict]:
        """获取订单支付记录"""
        with TransactionManager() as tm:
            order_id = self.get_id_by_uuid("order_info", order_uuid, tm.session)
            if not order_id:
                raise BusinessException(40401, detail="订单不存在")

            order_obj = self.order_repository.get(id=order_id, session=tm.session)
            if not order_obj:
                raise BusinessException(40401, detail="订单不存在")

            payments = self.repository.list_by_order_id(order_obj.id, session=tm.session)
            return [self._transform_payment(p) for p in payments]

    def _transform_payment(self, obj) -> dict:
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            result[column.name] = value
        return result


order_payment_service = OrderPaymentService()
