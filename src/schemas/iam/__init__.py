"""
IAM 平台身份权限 Schema

包含：用户、角色、权限、部门等 Schema
"""

from .dept import DeptCreate, DeptResponse, DeptUpdate
from .permission import PermissionCreate, PermissionResponse, PermissionUpdate
from .role import RoleCreate, RoleResponse, RoleUpdate
from .user import (
    UpdatePassword,
    UserCreate,
    UserListResponseItem,
    UserResponse,
    UserUpdate,
)

__all__ = [
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
    # Dept
    "DeptCreate",
    "DeptUpdate",
    "DeptResponse",
]
