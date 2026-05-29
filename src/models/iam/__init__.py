"""
身份权限体系模型

包含：用户、部门、角色、资源、手机号绑定等模型
关联表在 associations.py 中定义，不在此处导出
"""

from .dept import Dept, DeptClosure
from .phone_binding import PhoneBinding
from .resource import Resource
from .role import Role
from .user import User

__all__ = [
    "User",
    "Dept",
    "DeptClosure",
    "Role",
    "Resource",
    "PhoneBinding",
]
