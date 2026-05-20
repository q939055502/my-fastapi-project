# api/v1/tenants/user_tenant.py
from fastapi import APIRouter, Depends, Request
from typing import List

from src.core.dependency import AuthControl
from src.core.response import success, success_page
from src.services.sys.user_tenant_service import user_tenant_service
from src.schemas.sys.user_tenant import (
    TenantCreate,
    TenantUpdate,
    UserTenantListResponse,
    TenantMemberResponse
)
from src.core.rate_limit import apply_rate_limit
from src.models.sys.user import User

router = APIRouter(prefix="/user-tenants", tags=["用户-租户关联"])


@router.post("/create", summary="创建租户")
@apply_rate_limit("10/minute")
def create_tenant(request: Request, tenant_in: TenantCreate, current_user: User = Depends(AuthControl.is_authed)):
    """创建新租户，当前用户自动成为户主"""
    tenant = user_tenant_service.create_tenant(tenant_in, current_user.id)
    return success(data=tenant, msg="租户创建成功")


@router.post("/{tenant_id}/invite", summary="邀请用户加入租户")
@apply_rate_limit("30/minute")
def invite_user_to_tenant(
    request: Request,
    tenant_id: int,
    user_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    """邀请用户加入租户（需要是租户成员）"""
    result = user_tenant_service.invite_user_to_tenant(tenant_id, user_id, current_user.id)
    return success(data=result, msg="邀请成功")


@router.get("/my-tenants", summary="获取我的租户列表")
@apply_rate_limit("60/minute")
def get_my_tenants(request: Request, current_user: User = Depends(AuthControl.is_authed)):
    """获取当前用户关联的所有租户"""
    tenants = user_tenant_service.get_user_tenants(current_user.id)
    return success(data=tenants)


@router.get("/{tenant_id}/members", summary="获取租户成员列表")
@apply_rate_limit("60/minute")
def get_tenant_members(request: Request, tenant_id: int, current_user: User = Depends(AuthControl.is_authed)):
    """获取指定租户的所有成员"""
    if not user_tenant_service.check_user_in_tenant(current_user.id, tenant_id):
        return success(data=[], msg="您不在此租户中")

    members = user_tenant_service.get_tenant_members(tenant_id)
    return success(data=members)


@router.get("/{tenant_id}/relation", summary="获取用户在租户中的身份")
@apply_rate_limit("60/minute")
def get_user_tenant_relation(
    request: Request,
    tenant_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    """获取用户在指定租户中的关联信息"""
    relation = user_tenant_service.get_user_current_tenant(current_user.id, tenant_id)
    return success(data=relation)


@router.delete("/{tenant_id}/members/{user_id}", summary="移除租户成员")
@apply_rate_limit("30/minute")
def remove_tenant_member(
    request: Request,
    tenant_id: int,
    user_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    """从租户移除成员（需要是户主）"""
    user_tenant_service.remove_user_from_tenant(tenant_id, user_id, current_user.id)
    return success(msg="成员移除成功")
