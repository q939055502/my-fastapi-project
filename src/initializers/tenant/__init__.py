"""租户初始化器"""

from .tenant_dict_initializer import init_tenant_dict
from .tenant_initializer import init_default_tenant, init_plans

__all__ = [

    "init_plans",

    "init_default_tenant",

    "init_tenant_dict",

]

