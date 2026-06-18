"""
订单业务枚举

- BuyerTypeEnum: 购买主体类型
- ProductTypeEnum: 商品类型
- OrderTypeEnum: 订单类型
- CycleTypeEnum: 周期类型
- PayStatusEnum: 支付状态
- OrderStatusEnum: 订单状态
- OrderSourceEnum: 订单来源
- PaymentMethodEnum: 支付方式
- RefundStatusEnum: 退款状态
- OrderActionEnum: 订单操作动作
- OperatorTypeEnum: 操作人类型
"""

from enum import Enum


class BuyerTypeEnum(Enum):
    """购买主体类型"""
    TENANT = "tenant"
    USER = "user"


class ProductTypeEnum(Enum):
    """商品类型"""
    MEMBER = "member"
    SERVICE = "service"


class OrderTypeEnum(Enum):
    """订单类型"""
    NEW = "new"
    RENEW = "renew"
    UPGRADE = "upgrade"


class CycleTypeEnum(Enum):
    """周期类型"""
    MONTH = "month"
    YEAR = "year"


class PayStatusEnum(Enum):
    """支付状态"""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"
    EXPIRED = "expired"


class OrderStatusEnum(Enum):
    """订单状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderSourceEnum(Enum):
    """订单来源"""
    MANUAL = "manual"
    AUTO = "auto"
    TRIAL_UPGRADE = "trial_upgrade"


class PaymentMethodEnum(Enum):
    """支付方式"""
    WECHAT = "wechat"
    ALIPAY = "alipay"
    MANUAL = "manual"
    BANK_TRANSFER = "bank_transfer"


class RefundStatusEnum(Enum):
    """退款状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESS = "success"
    FAILED = "failed"


class RefundMethodEnum(Enum):
    """退款方式"""
    ORIGINAL = "original"
    ALIPAY = "alipay"
    WECHAT = "wechat"
    OTHER = "other"


class OrderActionEnum(Enum):
    """订单操作动作"""
    CREATE = "create"
    PAY = "pay"
    CANCEL = "cancel"
    REFUND = "refund"
    EXPIRE = "expire"
    EXTEND = "extend"
    UPGRADE = "upgrade"
    UPDATE = "update"


class OperatorTypeEnum(Enum):
    """操作人类型"""
    SYSTEM = "system"
    USER = "user"
    ADMIN = "admin"