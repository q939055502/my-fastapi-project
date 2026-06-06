

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
    Order,
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
    TenantPermission,
    TenantPlan,
    TenantQuota,
    TenantRole,
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
    "TenantPlan",
    "TenantConfig",
    "TenantQuota",
    "TenantUsage",
    "TenantHourlyUsage",
    "TenantMember",
    "TenantRole",
    "TenantPermission",
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
    # Order
    "Order",
    "OrderPayment",
    "OrderRefund",
    "OrderLog",
]
