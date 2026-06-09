"""
平台 Schema

包含：IAM 身份权限体系、System 系统基础模块
"""

# IAM 平台身份权限
from .dept import DeptCreate, DeptResponse, DeptUpdate
from .role_permission import (
    RolePermissionCreate,
    RolePermissionResponse,
    RolePermissionUpdate,
)
from .role_subject import (
    RoleSubjectCreate,
    RoleSubjectResponse,
    RoleSubjectUpdate,
)

# System 系统基础
from .dict_data import DictDataCreate, DictDataResponse, DictDataUpdate
from .dict_type import DictTypeCreate, DictTypeResponse, DictTypeUpdate
from .permission import PermissionCreate, PermissionResponse, PermissionUpdate
from .role import RoleCreate, RoleResponse, RoleUpdate
from .system_config import SystemConfigUpdate
from .tenant_plan import TenantPlanCreate, TenantPlanResponse, TenantPlanUpdate
from .user import (
    UpdatePassword,
    UserCreate,
    UserListResponseItem,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # IAM
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponseItem",
    "UpdatePassword",
    # Role
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    # Permission
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionResponse",
    # RolePermission
    "RolePermissionCreate",
    "RolePermissionUpdate",
    "RolePermissionResponse",
    # RoleSubject
    "RoleSubjectCreate",
    "RoleSubjectUpdate",
    "RoleSubjectResponse",
    # Dept
    "DeptCreate",
    "DeptUpdate",
    "DeptResponse",
    # System
    "DictTypeCreate",
    "DictTypeUpdate",
    "DictTypeResponse",
    "DictDataCreate",
    "DictDataUpdate",
    "DictDataResponse",
    "SystemConfigUpdate",
    "TenantPlanCreate",
    "TenantPlanUpdate",
    "TenantPlanResponse",
]
