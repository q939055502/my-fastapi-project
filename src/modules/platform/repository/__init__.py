from .dept_repository import dept_repository
from .dict_data_repository import dict_data_repository
from .dict_type_repository import dict_type_repository
from .file_mapping_repository import file_mapping_repository
from .permission_repository import permission_repository
from .role_repository import role_repository
from .system_config_repository import system_config_repository
from .user_repository import user_repository

__all__ = [
    "user_repository",
    "role_repository",
    "permission_repository",
    "dept_repository",
    "dict_data_repository",
    "dict_type_repository",
    "file_mapping_repository",
    "system_config_repository",
]
