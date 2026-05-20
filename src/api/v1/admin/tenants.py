"""
平台管理租户接口（超级管理员专用）
"""

from fastapi import APIRouter, Query, Depends, Request

from src.schemas.sys.tenant import TenantCreate, TenantUpdate
from src.services.sys.tenant_service import tenant_service
from src.core.response import success, success_page
from src.core.dependency import PermissionControl
from src.core.rate_limit import apply_rate_limit


router = APIRouter()


@router.post("/", summary="创建租户")
@apply_rate_limit("10/minute")
def create_tenant(
    request: Request,
    tenant_in: TenantCreate,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_data = tenant_service.create_tenant(tenant_in)
    return success(data=tenant_data, msg="租户创建成功")


@router.put("/{tenant_id}", summary="更新租户")
@apply_rate_limit("30/minute")
def update_tenant(
    request: Request,
    tenant_id: int,
    tenant_in: TenantUpdate,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_service.update_tenant(tenant_id, tenant_in)
    return success(msg="租户更新成功")


@router.get("/list", summary="获取租户列表")
@apply_rate_limit("60/minute")
def list_tenants(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="租户名称"),
    status: int = Query(None, description="状态"),
    current_user = Depends(PermissionControl.has_permission),
):
    total, data = tenant_service.get_tenant_list(
        page=page,
        page_size=page_size,
        name=name,
        status=status,
    )
    return success_page(data=data, total=total, page=page, page_size=page_size)


@router.get("/{tenant_id}", summary="获取租户详情")
@apply_rate_limit("60/minute")
def get_tenant(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_data = tenant_service.get_tenant_detail(tenant_id)
    return success(data=tenant_data)


@router.delete("/{tenant_id}", summary="删除租户")
@apply_rate_limit("10/minute")
def delete_tenant(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_service.delete_tenant(tenant_id)
    return success(msg="租户删除成功")
