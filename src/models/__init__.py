

"""
Models Package - 统一导出所有业务模型
"""
from src.models.base import (
    BaseModel,
    RemarkMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDModel,
)

# Order 订单模块
from src.models.order import (
    OrderInfo,
    OrderLog,
    OrderPayment,
    OrderRefund,
)

# IAM 身份权限体系
# System 系统基础模块
from src.models.platform import (
    AccountBind,
    AuditLog,
    Dept,
    DeptClosure,
    DictData,
    DictType,
    FileMapping,
    LoginLog,
    OperationLog,
    Permission,
    Role,
    SystemConfig,
    TenantPlan,
    User,
)

# Tenant 多租户核心
from src.models.tenant import (
    Tenant,
    TenantConfig,
    TenantDictData,
    TenantDictType,
    TenantHourlyUsage,
    TenantInvite,
    TenantMember,
    TenantQuota,
    TenantUsage,
)

__all__ = [
    # Base
    "BaseModel",
    "UUIDModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "RemarkMixin",
    # IAM
    "User",
    "Role",
    "Permission",
    "Dept",
    "DeptClosure",
    "AccountBind",
    # Tenant
    "Tenant",
    "TenantConfig",
    "TenantQuota",
    "TenantUsage",
    "TenantHourlyUsage",
    "TenantMember",
    "TenantInvite",
    "TenantDictType",
    "TenantDictData",
    # System
    "DictType",
    "DictData",
    "LoginLog",
    "OperationLog",
    "SystemConfig",
    "AuditLog",
    "FileMapping",
    "TenantPlan",
    # Order
    "OrderInfo",
    "OrderPayment",
    "OrderRefund",
    "OrderLog",
]
