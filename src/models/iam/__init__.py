"""
身份权限体系模型

包含：用户、部门、角色、权限、用户绑定等模型
关联表在 associations.py 中定义，不在此处导出
"""

from .dept import Dept, DeptClosure
from .permission import Permission
from .role import Role
from .user import User
from .user_bind import UserBind

__all__ = [
    "User",
    "Dept",
    "DeptClosure",
    "Role",
    "Permission",
    "UserBind",
]
