"""
平台模型

包含：IAM 身份权限体系、System 系统基础模块
"""

# IAM 身份权限体系
# System 系统基础模块
from .account_bind import AccountBind
from .audit_log import AuditLog
from .dept import Dept, DeptClosure
from .dict_data import DictData
from .dict_type import DictType
from .file_mapping import FileMapping
from .login_log import LoginLog
from .operation_log import OperationLog
from .rbac import Permission, Role, RolePermission, RoleSubject
from .system_config import SystemConfig
from .tenant_plan import TenantPlan
from .user import User

__all__ = [
    # IAM
    "User",
    "Dept",
    "DeptClosure",
    "Role",
    "Permission",
    "RolePermission",
    "RoleSubject",
    "AccountBind",
    # System
    "AuditLog",
    "DictData",
    "DictType",
    "FileMapping",
    "LoginLog",
    "OperationLog",
    "SystemConfig",
    "TenantPlan",
]
