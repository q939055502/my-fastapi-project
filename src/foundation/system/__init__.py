"""
System 系统通用功能模块

包含：
- 用户管理（平台用户）
- 组织架构管理
- 字典数据管理
- 系统配置管理
- 审计日志
- 文件管理
- 租户套餐管理
"""

from .service import (
    UserService,
    user_service,
    UserAdminService,
    user_admin_service,
    OrgService,
    org_service,
    AuditLogService,
    audit_log_service,
    FileService,
    file_service,
    SystemConfigService,
    system_config_service,
    TenantPlanService,
    tenant_plan_service,
)
from .repository import (
    user_repository,
    org_repository,
    dict_data_repository,
    dict_type_repository,
    file_mapping_repository,
    system_config_repository,
    tenant_plan_repository,
)

__all__ = [
    "UserService",
    "user_service",
    "UserAdminService",
    "user_admin_service",
    "OrgService",
    "org_service",
    "AuditLogService",
    "audit_log_service",
    "FileService",
    "file_service",
    "SystemConfigService",
    "system_config_service",
    "TenantPlanService",
    "tenant_plan_service",
    "user_repository",
    "org_repository",
    "dict_data_repository",
    "dict_type_repository",
    "file_mapping_repository",
    "system_config_repository",
    "tenant_plan_repository",
]