"""
API v1 版本路由注册

架构设计：
- admin/    : 平台超管专属接口（管理所有租户）
- tenant/   : 租户管理员接口（管理当前租户）
- auth/     : 认证接口（登录、注册、Token刷新）
- public/   : 公开接口（无需认证）
- me/       : 个人中心（当前用户）
- common/   : 公共共用接口（文件等）
"""

from fastapi import APIRouter, Depends

from src.core.auth import AuthControl, PermissionControl

# ============================================================
# 🏢 平台超管专属接口（admin）
# ============================================================
from .admin.auditlog import router as admin_auditlog_router
from .admin.depts import router as admin_depts_router
from .admin.plans import router as admin_plans_router
from .admin.resources import router as admin_resources_router
from .admin.roles import router as admin_roles_router
from .admin.settings import router as admin_settings_router
from .admin.tenants import router as admin_tenants_router
from .admin.users import router as admin_users_router

# ============================================================
# 🔐 认证接口
# ============================================================
from .auth import auth_router

# ============================================================
# 📄 通用文件接口
# ============================================================
from .common.files import router as common_files_router

# ============================================================
# 👤 个人中心接口
# ============================================================
from .me.profile import router as me_profile_router

# ============================================================
# 🔓 公开接口（无需认证）
# ============================================================
from .public.info import router as public_info_router

# ============================================================
# 👥 租户管理员接口（tenant）
# ============================================================
from .tenant import (
    tenant_info_router,
    tenant_invite_router,
    tenant_manage_router,
    tenant_members_router,
    tenant_permissions_router,
    tenant_roles_router,
    tenant_settings_router,
    user_tenant_router,
)

# ============================================================
# 📱 用户绑定接口
# ============================================================
from .user_binds import router as user_binds_router

v1_router = APIRouter()

# ============================================================
# 🔓 公开接口（无需认证）
# ============================================================
v1_router.include_router(public_info_router, prefix="/public")
v1_router.include_router(auth_router, prefix="/auth")

# ============================================================
# 🏢 平台超管专属接口（需平台权限）
# ============================================================
admin_deps = [Depends(PermissionControl.has_permission)]
v1_router.include_router(admin_tenants_router, prefix="/admin/tenants", dependencies=admin_deps)
v1_router.include_router(admin_users_router, prefix="/admin/users", dependencies=admin_deps)
v1_router.include_router(admin_roles_router, prefix="/admin/roles", dependencies=admin_deps)
v1_router.include_router(admin_depts_router, prefix="/admin/depts", dependencies=admin_deps)
v1_router.include_router(admin_resources_router, prefix="/admin/resources", dependencies=admin_deps)
v1_router.include_router(admin_plans_router, prefix="/admin/plans", dependencies=admin_deps)
v1_router.include_router(admin_auditlog_router, prefix="/admin/auditlog", dependencies=admin_deps)
v1_router.include_router(admin_settings_router, prefix="/admin/settings", dependencies=admin_deps)

# ============================================================
# 👥 租户管理员接口（需租户成员权限）
# ============================================================
tenant_deps = [Depends(AuthControl.is_authed)]
v1_router.include_router(tenant_info_router, prefix="/tenant/info", dependencies=tenant_deps)
v1_router.include_router(tenant_members_router, prefix="/tenant/members", dependencies=tenant_deps)
v1_router.include_router(tenant_roles_router, prefix="/tenant/roles", dependencies=tenant_deps)
v1_router.include_router(tenant_permissions_router, prefix="/tenant/permissions", dependencies=tenant_deps)
v1_router.include_router(tenant_invite_router, prefix="/tenant/invite", dependencies=tenant_deps)
v1_router.include_router(tenant_manage_router, prefix="/tenant/manage", dependencies=tenant_deps)
v1_router.include_router(tenant_settings_router, prefix="/tenant/settings", dependencies=tenant_deps)
v1_router.include_router(user_tenant_router, prefix="/tenant/user-tenants", dependencies=tenant_deps)

# ============================================================
# 👤 个人中心接口（需登录）
# ============================================================
v1_router.include_router(me_profile_router, prefix="/me", dependencies=[Depends(AuthControl.is_authed)])

# ============================================================
# 📱 用户绑定接口（需登录）
# ============================================================
v1_router.include_router(user_binds_router, prefix="/user-binds", dependencies=[Depends(AuthControl.is_authed)])

# ============================================================
# 📄 通用文件接口（需登录）
# ============================================================
v1_router.include_router(common_files_router, prefix="/common/files", dependencies=[Depends(AuthControl.is_authed)])


__all__ = ["v1_router"]
