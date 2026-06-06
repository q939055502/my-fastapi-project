
"""平台相关初始化器"""
from .config_initializer import init_system_config
from .dept_initializer import init_depts
from .dict_initializer import init_dict
from .menu_initializer import init_menus
from .permission_initializer import init_permissions
from .region_initializer import init_regions
from .role_initializer import init_roles
from .user_initializer import init_superuser

__all__ = [
    "init_superuser",
    "init_roles",
    "init_permissions",
    "init_menus",
    "init_depts",
    "init_dict",
    "init_system_config",
    "init_regions",
]

