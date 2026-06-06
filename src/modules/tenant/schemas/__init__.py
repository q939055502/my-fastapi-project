"""
Tenant 租户级 Schema

包含：租户、租户套餐、租户成员、租户角色、租户权限、邀请、字典等 Schema
"""

from .dict_data import (
    TenantDictDataCreate,
    TenantDictDataResponse,
    TenantDictDataUpdate,
)
from .dict_type import (
    TenantDictTypeCreate,
    TenantDictTypeResponse,
    TenantDictTypeUpdate,
)
from .invite import ApplyJoin, AuditJoin, InviteGenerate, InviteResponse
from .member import (
    TenantMemberCreate,
    TenantMemberResponse,
    TenantMemberRoleUpdate,
    TenantMemberUpdate,
)
from .permission import (
    TenantPermissionCreate,
    TenantPermissionResponse,
    TenantPermissionUpdate,
)
from .role import TenantRoleCreate, TenantRoleResponse, TenantRoleUpdate
from .tenant import TenantCreate, TenantResponse, TenantUpdate
from .tenant_plan import TenantPlanCreate, TenantPlanResponse, TenantPlanUpdate

__all__ = [
    # Tenant
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    # TenantPlan
    "TenantPlanCreate",
    "TenantPlanUpdate",
    "TenantPlanResponse",
    # Member
    "TenantMemberCreate",
    "TenantMemberUpdate",
    "TenantMemberResponse",
    "TenantMemberRoleUpdate",
    # Role
    "TenantRoleCreate",
    "TenantRoleUpdate",
    "TenantRoleResponse",
    # Permission
    "TenantPermissionCreate",
    "TenantPermissionUpdate",
    "TenantPermissionResponse",
    # Invite
    "InviteGenerate",
    "ApplyJoin",
    "AuditJoin",
    "InviteResponse",
    # Dict
    "TenantDictTypeCreate",
    "TenantDictTypeUpdate",
    "TenantDictTypeResponse",
    "TenantDictDataCreate",
    "TenantDictDataUpdate",
    "TenantDictDataResponse",
]
