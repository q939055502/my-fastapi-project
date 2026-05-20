"""
API v1 版本路由注册
"""

from fastapi import APIRouter, Depends

from src.core.dependency import PermissionControl, AuthControl

# 公开接口（无需认证）
from .public.info import router as public_info_router

# 认证接口（登录、token管理）
from .auth import router as auth_router

# 平台超管专属接口
from .admin.auditlog import router as admin_auditlog_router
from .admin.tenants import router as admin_tenants_router
from .admin.plans import router as admin_plans_router
from .admin.settings import router as admin_settings_router

# 通用资源接口（所有角色使用同一套，通过权限控制）
from .users import router as users_router
from .roles import router as roles_router
from .depts import router as depts_router
from .resources import router as resources_router
from .tenant import router as common_tenant_router

# 个人中心接口
from .me.profile import router as me_profile_router

# 通用接口（需登录）
from .common.files import router as common_files_router

# SaaS 租户关联接口
from .tenants.user_tenant import router as user_tenant_router


v1_router = APIRouter()

# ============================================================
# 🔓 公开接口（无需认证）
# ============================================================
v1_router.include_router(public_info_router, prefix="/public")

# ============================================================
# 🔐 认证接口
# ============================================================
v1_router.include_router(auth_router, prefix="/auth")

# ============================================================
# 🏢 平台超管专属接口（需权限）
# ============================================================
v1_router.include_router(admin_tenants_router, prefix="/admin/tenants", dependencies=[Depends(PermissionControl.has_permission)])
v1_router.include_router(admin_plans_router, prefix="/admin/plans", dependencies=[Depends(PermissionControl.has_permission)])
v1_router.include_router(admin_auditlog_router, prefix="/admin/auditlog", dependencies=[Depends(PermissionControl.has_permission)])
v1_router.include_router(admin_settings_router, prefix="/admin/settings", dependencies=[Depends(PermissionControl.has_permission)])

# ============================================================
# 📦 通用资源接口（需权限，所有角色共用）
# ============================================================
v1_router.include_router(users_router, prefix="/users", dependencies=[Depends(PermissionControl.has_permission)])
v1_router.include_router(roles_router, prefix="/roles", dependencies=[Depends(PermissionControl.has_permission)])
v1_router.include_router(depts_router, prefix="/depts", dependencies=[Depends(PermissionControl.has_permission)])
v1_router.include_router(resources_router, prefix="/resources", dependencies=[Depends(PermissionControl.has_permission)])
v1_router.include_router(common_tenant_router, prefix="/tenant", dependencies=[Depends(PermissionControl.has_permission)])

# ============================================================
# 👤 个人中心接口（需登录）
# ============================================================
v1_router.include_router(me_profile_router, prefix="/me", dependencies=[Depends(AuthControl.is_authed)])

# ============================================================
# 🔄 通用接口（需登录）
# ============================================================
v1_router.include_router(common_files_router, prefix="/common/files", dependencies=[Depends(AuthControl.is_authed)])

# ============================================================
# 🏢 SaaS 租户关联接口
# ============================================================
v1_router.include_router(user_tenant_router, prefix="/tenants", dependencies=[Depends(AuthControl.is_authed)])


__all__ = ["v1_router"]