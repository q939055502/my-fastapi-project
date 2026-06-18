"""
Models Package - 统一导出所有业务模型

设计原则：
1. 所有业务模型统一在 models 目录下管理
2. 按领域分组：platform（平台）、tenant（租户）、order（订单）
3. 从 models 顶层绝对导入，禁止直接导入深层子文件
"""
from src.models.base import BaseModel
from src.models.mixins import (
    RemarkMixin,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDModel,
)

# Platform 平台模型（IAM 身份权限体系、系统基础模块）
from src.models.platform import (
    AccountBind,
    AuditLog,
    DataScopeRule,
    DictData,
    DictType,
    FileMapping,
    LoginLog,
    OperationLog,
    Org,
    OrgClosure,
    Permission,
    Role,
    RolePermission,
    RoleSubject,
    SystemConfig,
    TenantPlan,
    User,
)

# Tenant 多租户核心模型
from src.models.tenant import (
    Tenant,
    Member,
    Invite,
    TenantConfig,
    Quota,
    Usage,
    HourlyUsage,
    OperLog,
    TenantDictType,
    TenantDictData,
)

# Order 订单模块模型
from src.models.order import (
    OrderInfo,
    OrderLog,
    OrderPayment,
    OrderRefund,
)

__all__ = [
    # Base
    "BaseModel",
    "UUIDModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "RemarkMixin",
    # Platform - IAM
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "RoleSubject",
    "DataScopeRule",
    "Org",
    "OrgClosure",
    "AccountBind",
    # Platform - System
    "DictType",
    "DictData",
    "LoginLog",
    "OperationLog",
    "SystemConfig",
    "AuditLog",
    "FileMapping",
    "TenantPlan",
    # Tenant
    "Tenant",
    "Member",
    "Invite",
    "TenantConfig",
    "Quota",
    "Usage",
    "HourlyUsage",
    "OperLog",
    "TenantDictType",
    "TenantDictData",
    # Order
    "OrderInfo",
    "OrderPayment",
    "OrderRefund",
    "OrderLog",
]