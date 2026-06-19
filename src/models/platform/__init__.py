"""
平台模型
包含:IAM 身份权限体系, 系统基础模块
"""

from .auth import AccountBind, AuditLog, LoginLog, OperationLog, User
from .file import FileMapping
from .rbac import DataScopeRule, Permission, Role, RolePermission, RoleSubject
from .system import DictData, DictType, Org, OrgClosure, SystemConfig, TenantPlan

__all__ = [
    # Auth
    "User",
    "AccountBind",
    "LoginLog",
    "OperationLog",
    "AuditLog",
    # System
    "Org",
    "OrgClosure",
    "DictType",
    "DictData",
    "SystemConfig",
    "TenantPlan",
    # File
    "FileMapping",
    # RBAC
    "Role",
    "Permission",
    "RolePermission",
    "RoleSubject",
    "DataScopeRule",
]
