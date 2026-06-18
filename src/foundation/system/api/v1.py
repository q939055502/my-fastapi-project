"""
System API v1 路由
"""
from fastapi import APIRouter, Depends
from src.foundation.iam import AuthControl, PermissionControl

from ..endpoints.info import router as public_info_router
from ..endpoints.me import router as me_router
from ..endpoints.account_bind import router as account_bind_router
from ..endpoints.files import router as common_files_router
from ..endpoints.admin_users import router as admin_users_router
from ..endpoints.orgs import router as admin_orgs_router
from ..endpoints.auditlog import router as admin_auditlog_router
from ..endpoints.settings import router as admin_settings_router
from ..endpoints.plans import router as admin_plans_router
from ..endpoints.dict import router as dict_router

system_v1_router = APIRouter()

admin_deps = [Depends(PermissionControl.has_permission)]

system_v1_router.include_router(public_info_router, prefix="/public")
system_v1_router.include_router(me_router, prefix="/me", dependencies=[Depends(AuthControl.is_authed)])
system_v1_router.include_router(account_bind_router, prefix="/account-binds", dependencies=[Depends(AuthControl.is_authed)])
system_v1_router.include_router(common_files_router, prefix="/common/files", dependencies=[Depends(AuthControl.is_authed)])

system_v1_router.include_router(admin_users_router, prefix="/admin/users", dependencies=admin_deps)
system_v1_router.include_router(admin_orgs_router, prefix="/admin/orgs", dependencies=admin_deps)
system_v1_router.include_router(admin_auditlog_router, prefix="/admin/auditlog", dependencies=admin_deps)
system_v1_router.include_router(admin_settings_router, prefix="/admin/settings", dependencies=admin_deps)
system_v1_router.include_router(admin_plans_router, prefix="/admin/plans", dependencies=admin_deps)
system_v1_router.include_router(dict_router, prefix="/admin/dict", dependencies=admin_deps)

__all__ = ["system_v1_router"]