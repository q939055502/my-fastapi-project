"""
Tenant 租户级 Schema

包含：租户、租户成员、租户角色、租户权限、邀请、字典等 Schema
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
from .tenant import TenantCreate, TenantResponse, TenantUpdate

__all__ = [
    # Tenant
    "TenantCreate",
    "TenantUpdate",
    "TenantResponse",
    # Member
    "TenantMemberCreate",
    "TenantMemberUpdate",
    "TenantMemberResponse",
    "TenantMemberRoleUpdate",
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
