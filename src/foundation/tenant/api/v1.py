"""
租户模块 API v1 路由
"""
from fastapi import APIRouter, Depends
from src.foundation.iam import AuthControl

from ..endpoints.info import router as tenant_info_router
from ..endpoints.invite import router as tenant_invite_router
from ..endpoints.members import router as tenant_members_router
from ..endpoints.settings import router as tenant_settings_router
from ..endpoints.tenant_manage import router as tenant_manage_router
from ..endpoints.tenant_roles import router as tenant_roles_router
from ..endpoints.user_tenant import router as user_tenant_router

tenant_v1_router = APIRouter()

tenant_deps = [Depends(AuthControl.is_authed)]

tenant_v1_router.include_router(tenant_info_router, prefix="/tenant/info", dependencies=tenant_deps)
tenant_v1_router.include_router(tenant_members_router, prefix="/tenant/members", dependencies=tenant_deps)
tenant_v1_router.include_router(tenant_invite_router, prefix="/tenant/invite", dependencies=tenant_deps)
tenant_v1_router.include_router(tenant_manage_router, prefix="/tenant/manage", dependencies=tenant_deps)
tenant_v1_router.include_router(tenant_settings_router, prefix="/tenant/settings", dependencies=tenant_deps)
tenant_v1_router.include_router(tenant_roles_router, prefix="/tenant/{tenant_uuid}/roles", dependencies=tenant_deps)
tenant_v1_router.include_router(user_tenant_router, prefix="/tenant/user-tenants", dependencies=tenant_deps)

__all__ = ["tenant_v1_router"]
