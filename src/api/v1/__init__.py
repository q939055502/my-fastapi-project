"""
API v1 版本路由注册

架构设计：
- admin/    : 平台超管专属接口（管理所有租户）
- client/   : 租户成员接口（管理当前租户）
- common/   : 公共共用接口（个人中心、认证等）
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
# 🔄 公共共用接口（common）
# ============================================================
# 认证接口
from .auth import router as auth_router
from .client.members import router as client_members_router

# ============================================================
# 👥 租户成员接口（client）
# ============================================================
from .client.tenant import router as client_tenant_router

# 通用文件接口
from .common.files import router as common_files_router

# 个人中心
from .me.profile import router as me_profile_router

# 手机号绑定
from .phone_bindings import router as phone_bindings_router

# 公开接口
from .public.info import router as public_info_router

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
# 👥 租户成员接口（需登录，租户内权限）
# ============================================================
client_deps = [Depends(AuthControl.is_authed)]
v1_router.include_router(client_tenant_router, prefix="/client/tenant", dependencies=client_deps)
v1_router.include_router(client_members_router, prefix="/client/members", dependencies=client_deps)

# ============================================================
# 👤 个人中心接口（需登录）
# ============================================================
v1_router.include_router(me_profile_router, prefix="/me", dependencies=[Depends(AuthControl.is_authed)])

# ============================================================
# 📱 手机号绑定接口（需登录）
# ============================================================
v1_router.include_router(phone_bindings_router, prefix="/phone-bindings", dependencies=[Depends(AuthControl.is_authed)])

# ============================================================
# 📄 通用文件接口（需登录）
# ============================================================
v1_router.include_router(common_files_router, prefix="/common/files", dependencies=[Depends(AuthControl.is_authed)])


__all__ = ["v1_router"]
