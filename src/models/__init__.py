

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

# IAM 身份权限体系
from src.models.iam import (
    Dept,
    DeptClosure,
    Permission,
    Role,
    User,
    UserBind,
)

# Order 订单模块
from src.models.order import (
    Order,
    OrderLog,
    OrderPayment,
    OrderRefund,
)

# System 系统基础模块
from src.models.system import (
    AuditLog,
    DictData,
    DictType,
    FileMapping,
    LoginLog,
    OperationLog,
    SystemConfig,
)

# Tenant 多租户核心
from src.models.tenant import (
    Tenant,
    TenantConfig,
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
    "UserBind",
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
