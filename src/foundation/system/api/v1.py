"""
System API v1 路由
"""
from fastapi import APIRouter, Depends
from src.foundation.iam import AuthControl, require_auth, require_permission

from ..endpoints.account_bind import router as account_bind_router
from ..endpoints.admin_users import router as admin_users_router
from ..endpoints.auditlog import router as admin_auditlog_router
from ..endpoints.dict import router as dict_router
from ..endpoints.files import router as common_files_router
from ..endpoints.info import router as public_info_router
from ..endpoints.me import router as me_router
from ..endpoints.orgs import router as admin_orgs_router
from ..endpoints.plans import router as admin_plans_router
from ..endpoints.settings import router as admin_settings_router

system_v1_router = APIRouter(prefix="/system", tags=["系统"])

# 平台管理员依赖
platform_admin_deps = [require_permission("platform:admin:access")]

system_v1_router.include_router(public_info_router, prefix="/public")
system_v1_router.include_router(me_router, prefix="/me", dependencies=[require_auth])
system_v1_router.include_router(account_bind_router, prefix="/account-binds", dependencies=[require_auth])
system_v1_router.include_router(common_files_router, prefix="/common/files", dependencies=[require_auth])

system_v1_router.include_router(admin_users_router, prefix="/admin/users", dependencies=platform_admin_deps)
system_v1_router.include_router(admin_orgs_router, prefix="/admin/orgs", dependencies=platform_admin_deps)
system_v1_router.include_router(admin_auditlog_router, prefix="/admin/auditlog", dependencies=platform_admin_deps)
system_v1_router.include_router(admin_settings_router, prefix="/admin/settings", dependencies=platform_admin_deps)
system_v1_router.include_router(admin_plans_router, prefix="/admin/plans", dependencies=platform_admin_deps)
system_v1_router.include_router(dict_router, prefix="/admin/dict", dependencies=platform_admin_deps)

__all__ = ["system_v1_router"]
