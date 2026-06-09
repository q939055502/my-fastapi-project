"""
平台模块 API v1 路由
"""
from fastapi import APIRouter, Depends
from src.common.core.auth import PermissionControl

from ..endpoints.admin_users import router as admin_users_router
from ..endpoints.auditlog import router as admin_auditlog_router
from ..endpoints.depts import router as admin_depts_router
from ..endpoints.plans import router as admin_plans_router
from ..endpoints.resources import router as admin_resources_router
from ..endpoints.roles import router as admin_roles_router
from ..endpoints.settings import router as admin_settings_router
from ..endpoints.tenants import router as admin_tenants_router

platform_v1_router = APIRouter()

admin_deps = [Depends(PermissionControl.has_permission)]

platform_v1_router.include_router(admin_tenants_router, prefix="/admin/tenants", dependencies=admin_deps)
platform_v1_router.include_router(admin_users_router, prefix="/admin/users", dependencies=admin_deps)
platform_v1_router.include_router(admin_roles_router, prefix="/admin/roles", dependencies=admin_deps)
platform_v1_router.include_router(admin_depts_router, prefix="/admin/depts", dependencies=admin_deps)
platform_v1_router.include_router(admin_resources_router, prefix="/admin/resources", dependencies=admin_deps)
platform_v1_router.include_router(admin_plans_router, prefix="/admin/plans", dependencies=admin_deps)
platform_v1_router.include_router(admin_auditlog_router, prefix="/admin/auditlog", dependencies=admin_deps)
platform_v1_router.include_router(admin_settings_router, prefix="/admin/settings", dependencies=admin_deps)

__all__ = ["platform_v1_router"]
