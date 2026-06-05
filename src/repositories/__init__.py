"""
Repositories Package - 统一导出所有 Repository
"""

from .base import GenericRepository

# IAM 平台身份权限
from .iam import (
    dept_repository,
    permission_repository,
    role_repository,
    user_repository,
)

# System 系统级
from .system import (
    dict_data_repository,
    dict_type_repository,
    file_mapping_repository,
    system_config_repository,
)

# Tenant 租户级
from .tenant import (
    tenant_invite_repository,
    tenant_member_repository,
    tenant_permission_repository,
    tenant_plan_repository,
    tenant_repository,
    tenant_role_repository,
)

__all__ = [
    # Base
    "GenericRepository",
    # IAM
    "user_repository",
    "role_repository",
    "permission_repository",
    "dept_repository",
    # Tenant
    "tenant_repository",
    "tenant_plan_repository",
    "tenant_member_repository",
    "tenant_role_repository",
    "tenant_permission_repository",
    "tenant_invite_repository",
    # System
    "dict_type_repository",
    "dict_data_repository",
    "file_mapping_repository",
    "system_config_repository",
]
