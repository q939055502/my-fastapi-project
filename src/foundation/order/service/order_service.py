from datetime import datetime

from src.core.base.service_base import BaseService
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.order.enums import (
    OrderActionEnum,
    OrderStatusEnum,
    PayStatusEnum,
)
from src.foundation.order.repository import (
    order_log_repository,
    order_repository,
)
from src.foundation.order.schemas.order import OrderCreate, OrderUpdate
from src.models.order import OrderLog


class OrderService(BaseService):
    """订单服务"""

    def __init__(self):
        super().__init__()
        self.repository = order_repository
        self.log_repository = order_log_repository

    def create_order(self, order_in: OrderCreate, operator_id: int = None, operator_name: str = None) -> dict:
        """创建订单"""
        with TransactionManager() as tm:
            order_no = self.repository.generate_order_no()
            order_data = order_in.model_dump(exclude_unset=True)
            order_data["order_no"] = order_no
            order_data["pay_status"] = PayStatusEnum.PENDING.value
            order_data["order_status"] = OrderStatusEnum.PENDING.value

            new_order = self.repository.create(obj_in=order_data, session=tm.session)
            tm.flush()

            # 记录操作日志
            self._write_log(
                order_id=new_order.id,
                action=OrderActionEnum.CREATE.value,
                before_pay_status=None,
                after_pay_status=new_order.pay_status,
                before_order_status=None,
                after_order_status=new_order.order_status,
                operator_id=operator_id,
                operator_name=operator_name,
                detail=f"创建订单:{order_no}",
                session=tm.session,
            )

            tm.commit()

            return self._transform_order(new_order)

    def get_order_detail(self, order_uuid: str) -> dict:
        """获取订单详情"""
        with TransactionManager() as tm:
            order_id = self.get_id_by_uuid("order_info", order_uuid, tm.session)
            if not order_id:
                raise BusinessException(40401, detail="订单不存在")

            order_obj = self.repository.get(id=order_id, session=tm.session)
            if not order_obj:
                raise BusinessException(40401, detail="订单不存在")

            return self._transform_order(order_obj)

    def list_orders(
        self,
        page: int = 1,
        page_size: int = 10,
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
    ) -> tuple[int, list[dict]]:
        """订单列表查询"""
        with TransactionManager() as tm:
            total, items = self.repository.list_orders(
                page=page,
                page_size=page_size,
                session=tm.session,
                buyer_type=buyer_type,
                buyer_id=buyer_id,
                product_type=product_type,
                product_id=product_id,
                order_type=order_type,
                pay_status=pay_status,
                order_status=order_status,
                order_no=order_no,
                start_time=start_time,
                end_time=end_time,
            )

            data = [self._transform_order(item) for item in items]
            return total, data

    def update_order(self, order_uuid: str, order_in: OrderUpdate) -> dict:
        """更新订单"""
        with TransactionManager() as tm:
            order_id = self.get_id_by_uuid("order_info", order_uuid, tm.session)
            if not order_id:
                raise BusinessException(40401, detail="订单不存在")

            order_obj = self.repository.get(id=order_id, session=tm.session)
            if not order_obj:
                raise BusinessException(40401, detail="订单不存在")

            before_pay = order_obj.pay_status
            before_order = order_obj.order_status

            update_data = order_in.model_dump(exclude_unset=True, exclude_none=True)
            self.repository.update(id=order_obj.id, obj_in=update_data, session=tm.session)
            tm.flush()

            # 记录变更日志
            after_pay = update_data.get("pay_status", before_pay)
            after_order = update_data.get("order_status", before_order)
            if before_pay != after_pay or before_order != after_order:
                self._write_log(
                    order_id=order_obj.id,
                    action=OrderActionEnum.UPDATE.value,
                    before_pay_status=before_pay,
                    after_pay_status=after_pay,
                    before_order_status=before_order,
                    after_order_status=after_order,
                    detail="更新订单",
                    session=tm.session,
                )

            tm.commit()

            return self._transform_order(order_obj)

    def cancel_order(self, order_uuid: str, reason: str = None, operator_id: int = None, operator_name: str = None) -> None:
        """取消订单"""
        with TransactionManager() as tm:
            order_id = self.get_id_by_uuid("order_info", order_uuid, tm.session)
            if not order_id:
                raise BusinessException(40401, detail="订单不存在")

            order_obj = self.repository.get(id=order_id, session=tm.session)
            if not order_obj:
                raise BusinessException(40401, detail="订单不存在")

            if order_obj.pay_status == PayStatusEnum.PAID.value:
                raise BusinessException(40000, detail="已支付订单不能直接取消,请走退款流程")

            before_pay = order_obj.pay_status
            before_order = order_obj.order_status

            order_obj.pay_status = PayStatusEnum.CANCELLED.value
            order_obj.order_status = OrderStatusEnum.CANCELLED.value
            tm.flush()

            self._write_log(
                order_id=order_obj.id,
                action=OrderActionEnum.CANCEL.value,
                before_pay_status=before_pay,
                after_pay_status=order_obj.pay_status,
                before_order_status=before_order,
                after_order_status=order_obj.order_status,
                operator_id=operator_id,
                operator_name=operator_name,
                detail=f"取消订单:{reason or '无'}",
                session=tm.session,
            )

            tm.commit()

    def list_order_logs(self, order_uuid: str) -> list[dict]:
        """获取订单操作日志"""
        with TransactionManager() as tm:
            order_id = self.get_id_by_uuid("order_info", order_uuid, tm.session)
            if not order_id:
                raise BusinessException(40401, detail="订单不存在")

            order_obj = self.repository.get(id=order_id, session=tm.session)
            if not order_obj:
                raise BusinessException(40401, detail="订单不存在")

            logs = self.log_repository.list_by_order_id(order_obj.id, session=tm.session)
            return [self._transform_log(log) for log in logs]

    def _write_log(
        self,
        order_id: int,
        action: str,
        before_pay_status: str | None,
        after_pay_status: str | None,
        before_order_status: str | None,
        after_order_status: str | None,
        operator_id: int | None = None,
        operator_name: str | None = None,
        operator_type: str = "user",
        detail: str | None = None,
        session=None,
    ) -> None:
        """记录订单操作日志"""
        log = OrderLog(
            order_id=order_id,
            action=action,
            before_pay_status=before_pay_status,
            after_pay_status=after_pay_status,
            before_order_status=before_order_status,
            after_order_status=after_order_status,
            operator_id=operator_id,
            operator_name=operator_name,
            operator_type=operator_type,
            detail=detail,
        )
        session.add(log)

    def _transform_log(self, obj) -> dict:
        """转换日志为字典"""
        result = {}
        for column in obj.__table__.columns:
            value = getattr(obj, column.name)
            result[column.name] = value
        return result


order_service = OrderService()
