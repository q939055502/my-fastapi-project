"""
平台模型

包含：IAM 身份权限体系、System 系统基础模块
关联表在 associations.py 中定义，不在此处导出
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
from .permission import Permission
from .role import Role
from .system_config import SystemConfig
from .user import User

__all__ = [
    # IAM
    "User",
    "Dept",
    "DeptClosure",
    "Role",
    "Permission",
    "AccountBind",
    # System
    "AuditLog",
    "DictData",
    "DictType",
    "FileMapping",
    "LoginLog",
    "OperationLog",
    "SystemConfig",
]
