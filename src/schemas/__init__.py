"""
Schemas Package - 统一导出所有业务 Schema
"""

# Auth 认证
from src.schemas.auth import (
    JWTOut,
    JWTPayload,
    LoginRequest,
    LoginStep1Response,
    LoginStep2Response,
    RefreshTokenRequest,
    RegisterRequest,
    SelectTenantRequest,
)
from src.schemas.base import BaseSchema

# Common 公共
from src.schemas.common import PaginationResponse

# IAM 平台身份权限
from src.schemas.iam import (
    DeptCreate,
    DeptResponse,
    DeptUpdate,
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    UpdatePassword,
    UserCreate,
    UserListResponseItem,
    UserResponse,
    UserUpdate,
)

# System 系统级
from src.schemas.system import (
    DictDataCreate,
    DictDataResponse,
    DictDataUpdate,
    DictTypeCreate,
    DictTypeResponse,
    DictTypeUpdate,
    SystemConfigUpdate,
)

# Tenant 租户级
from src.schemas.tenant import (
    ApplyJoin,
    AuditJoin,
    InviteGenerate,
    InviteResponse,
    TenantCreate,
    TenantDictDataCreate,
    TenantDictDataResponse,
    TenantDictDataUpdate,
    TenantDictTypeCreate,
    TenantDictTypeResponse,
    TenantDictTypeUpdate,
    TenantMemberCreate,
    TenantMemberResponse,
    TenantMemberRoleUpdate,
    TenantMemberUpdate,
    TenantPermissionCreate,
    TenantPermissionResponse,
    TenantPermissionUpdate,
    TenantPlanCreate,
    TenantPlanResponse,
    TenantPlanUpdate,
    TenantResponse,
    TenantRoleCreate,
    TenantRoleResponse,
    TenantRoleUpdate,
    TenantUpdate,
)

__all__ = [
    # Base
    "BaseSchema",
    # IAM
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponseItem",
    "UpdatePassword",
    "RoleCreate",
    "RoleUpdate",
    "RoleResponse",
    "PermissionCreate",
    "PermissionUpdate",
    "PermissionResponse",
    "DeptCreate",
    "DeptUpdate",
    "DeptResponse",
    # Tenant
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    "TenantPlanCreate",
    "TenantPlanUpdate",
    "TenantPlanResponse",
    "TenantMemberCreate",
    "TenantMemberUpdate",
    "TenantMemberResponse",
    "TenantMemberRoleUpdate",
    "TenantRoleCreate",
    "TenantRoleUpdate",
    "TenantRoleResponse",
    "TenantPermissionCreate",
    "TenantPermissionUpdate",
    "TenantPermissionResponse",
    "InviteGenerate",
    "ApplyJoin",
    "AuditJoin",
    "InviteResponse",
    "TenantDictTypeCreate",
    "TenantDictTypeUpdate",
    "TenantDictTypeResponse",
    "TenantDictDataCreate",
    "TenantDictDataUpdate",
    "TenantDictDataResponse",
    # System
    "DictTypeCreate",
    "DictTypeUpdate",
    "DictTypeResponse",
    "DictDataCreate",
    "DictDataUpdate",
    "DictDataResponse",
    "SystemConfigUpdate",
    # Auth
    "LoginRequest",
    "LoginStep1Response",
    "LoginStep2Response",
    "SelectTenantRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
    "JWTOut",
    "JWTPayload",
    # Common
    "PaginationResponse",
]
