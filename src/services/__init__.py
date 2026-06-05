"""
Services Package - 统一导出所有 Service
"""

# Auth
from .auth import auth_service
from .base_service import BaseService

# IAM
from .iam import (
    dept_service,
    resource_service,
    role_service,
    user_service,
)

# System
from .system import (
    audit_log_service,
    file_service,
    system_config_service,
)

# Tenant
from .tenant import (
    tenant_plan_service,
    tenant_service,
    user_tenant_service,
)

__all__ = [
    # Base
    "BaseService",
    # IAM
    "user_service",
    "role_service",
    "dept_service",
    "resource_service",
    # Tenant
    "tenant_service",
    "tenant_plan_service",
    "user_tenant_service",
    # System
    "system_config_service",
    "file_service",
    "audit_log_service",
    # Auth
    "auth_service",
]
