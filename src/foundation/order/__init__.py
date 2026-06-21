"""
Order 订单模块

订单是跨域的通用基础业务能力,支撑整个系统的商业化运行:
- 平台为租户升级付�?- 平台对用户提供商�?服务
- 租户对租户成员提供商�?服务

设计原则�?1. 跨域通用:作为基础业务能力放在 foundation �?2. 单向依赖:依�?core 层和 foundation 其他模块
3. 完整链路:覆盖订单创建, 支付, 退款, 查询, 日�?"""

from .api.v1 import order_v1_router
from .enums import (
    BuyerTypeEnum,
    CycleTypeEnum,
    OperatorTypeEnum,
    OrderActionEnum,
    OrderSourceEnum,
    OrderStatusEnum,
    OrderTypeEnum,
    PaymentMethodEnum,
    PayStatusEnum,
    ProductTypeEnum,
    RefundMethodEnum,
    RefundStatusEnum,
)
from .service import (
    order_payment_service,
    order_refund_service,
    order_service,
)

__all__ = [
    # 路由
    "order_v1_router",
    # 服务
    "order_service",
    "order_payment_service",
    "order_refund_service",
    # 枚举
    "BuyerTypeEnum",
    "ProductTypeEnum",
    "OrderTypeEnum",
    "CycleTypeEnum",
    "PayStatusEnum",
    "OrderStatusEnum",
    "OrderSourceEnum",
    "PaymentMethodEnum",
    "RefundStatusEnum",
    "RefundMethodEnum",
    "OrderActionEnum",
    "OperatorTypeEnum",
]
