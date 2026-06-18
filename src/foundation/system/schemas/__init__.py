"""
System Schema

包含：用户、组织、字典、系统配置、租户套餐的 Schema
"""

from .user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponseItem,
    UpdatePassword,
)
from .org import OrgCreate, OrgUpdate, OrgResponse
from .dict_data import DictDataCreate, DictDataUpdate, DictDataResponse
from .dict_type import DictTypeCreate, DictTypeUpdate, DictTypeResponse
from .system_config import SystemConfigUpdate
from .tenant_plan import TenantPlanCreate, TenantPlanUpdate, TenantPlanResponse

__all__ = [
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserListResponseItem",
    "UpdatePassword",
    # Org
    "OrgCreate",
    "OrgUpdate",
    "OrgResponse",
    # Dict
    "DictDataCreate",
    "DictDataUpdate",
    "DictDataResponse",
    "DictTypeCreate",
    "DictTypeUpdate",
    "DictTypeResponse",
    # SystemConfig
    "SystemConfigUpdate",
    # TenantPlan
    "TenantPlanCreate",
    "TenantPlanUpdate",
    "TenantPlanResponse",
]