from .dept_repository import dept_repository
from .file_mapping_repository import file_mapping_repository
from .resource_repository import resource_repository
from .role_repository import role_repository
from .system_config_repository import system_config_repository
from .tenant_plan_repository import tenant_plan_repository
from .tenant_repository import tenant_repository
from .user_repository import user_repository

__all__ = [
    "dept_repository",
    "file_mapping_repository",
    "role_repository",
    "user_repository",
    "resource_repository",
    "tenant_repository",
    "tenant_plan_repository",
    "system_config_repository",
]
