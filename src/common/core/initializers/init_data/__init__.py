"""初始化数据模块"""
from .common.db_initializer import init_db
from .platform.user_initializer import init_superuser
from .platform.role_initializer import init_roles
from .platform.permission_initializer import init_permissions
from .platform.menu_initializer import init_menus
from .platform.dept_initializer import init_depts
from .platform.dict_initializer import init_dict
from .platform.config_initializer import init_system_config
from .platform.region_initializer import init_regions
from .tenant.tenant_initializer import init_default_tenant, init_plans
from .tenant.tenant_dict_initializer import init_tenant_dict

__all__ = [
    "init_db",
    "init_superuser",
    "init_roles",
    "init_permissions",
    "init_menus",
    "init_depts",
    "init_dict",
    "init_system_config",
    "init_regions",
    "init_plans",
    "init_default_tenant",
    "init_tenant_dict",
]
