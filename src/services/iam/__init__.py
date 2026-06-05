from .dept_service import DeptService, dept_service
from .permission_service import ResourceService, resource_service
from .role_service import RoleService, role_service
from .user_service import UserService, user_service

__all__ = [
    "UserService",
    "user_service",
    "RoleService",
    "role_service",
    "DeptService",
    "dept_service",
    "ResourceService",
    "resource_service",
]
