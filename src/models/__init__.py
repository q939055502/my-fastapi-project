
"""
Models Package
"""
from src.models.base import BaseModel, UUIDModel, TimestampMixin, SoftDeleteMixin, RemarkMixin
from src.models.sys import (
    User,
    Role,
    Resource,
    Dept,
    DeptClosure,
    Tenant,
    TenantPlan,
    TenantConfig,
    TenantQuota,
    DictType,
    DictData,
    AuditLog,
    LoginLog,
    OperationLog,
    FileMapping,
    SystemConfig,
    user_role_association,
    role_resource_association,
    user_tenant_association,
)

__all__ = [
    "BaseModel",
    "UUIDModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "RemarkMixin",
    "User",
    "Role",
    "Resource",
    "Dept",
    "DeptClosure",
    "Tenant",
    "TenantPlan",
    "TenantConfig",
    "TenantQuota",
    "DictType",
    "DictData",
    "AuditLog",
    "LoginLog",
    "OperationLog",
    "FileMapping",
    "SystemConfig",
    "user_role_association",
    "role_resource_association",
    "user_tenant_association",
]

