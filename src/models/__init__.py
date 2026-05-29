
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
    PhoneBinding,
    Resource,
    Role,
    User,
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
    TenantMember,
    TenantPlan,
    TenantQuota,
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
    "Resource",
    "Dept",
    "DeptClosure",
    "PhoneBinding",
    # Tenant
    "Tenant",
    "TenantPlan",
    "TenantConfig",
    "TenantQuota",
    "TenantMember",
    # System
    "DictType",
    "DictData",
    "LoginLog",
    "OperationLog",
    "SystemConfig",
    "AuditLog",
    "FileMapping",
]

