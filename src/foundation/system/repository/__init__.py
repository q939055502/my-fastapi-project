"""
System Repository

包含:用户仓库, 组织仓库, 字典数据仓库, 字典类型仓库, 文件映射仓库, 系统配置仓库, 租户套餐仓�?"""

from .dict_data_repository import dict_data_repository
from .dict_type_repository import dict_type_repository
from .file_mapping_repository import file_mapping_repository
from .org_repository import org_repository
from .system_config_repository import system_config_repository
from .tenant_plan_repository import tenant_plan_repository
from .user_repository import user_repository

__all__ = [
    "user_repository",
    "org_repository",
    "dict_data_repository",
    "dict_type_repository",
    "file_mapping_repository",
    "system_config_repository",
    "tenant_plan_repository",
]
