"""
平台管理租户接口（超级管理员专用）
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from src.foundation.iam import PermissionControl
from src.core.enums.response_code import ResponseCode
from src.core.plugins import apply_rate_limit
from src.core.response import gen_swagger_response, success, success_page
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.tenant.schemas.tenant import TenantCreate, TenantUpdate
from src.foundation.tenant.service.tenant_service import tenant_service

router = APIRouter(
    tags=["平台管理-租户"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/",
    summary="创建租户",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.DATA_ALREADY_EXIST],
            description="租户名称已存在"
        ),
    },
)
@apply_rate_limit("10/minute")
def create_tenant(
    request: Request,
    tenant_in: TenantCreate,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_data = tenant_service.create_tenant(tenant_in)
    return success(data=tenant_data, msg="租户创建成功")


@router.put(
    "/{tenant_uuid}",
    summary="更新租户",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="租户不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_tenant(
    request: Request,
    tenant_uuid: UUID,
    tenant_in: TenantUpdate,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_service.update_tenant(tenant_uuid, tenant_in)
    return success(msg="租户更新成功")


@router.get("/list", summary="获取租户列表")
@apply_rate_limit("60/minute")
def list_tenants(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="租户名称"),
    status: bool = Query(None, description="状态"),
    current_user = Depends(PermissionControl.has_permission),
):
    total, data = tenant_service.get_tenant_list(
        page=page,
        page_size=page_size,
        name=name,
        status=status,
    )
    return success_page(data=data, total=total, page=page, page_size=page_size)


@router.get(
    "/{tenant_uuid}",
    summary="获取租户详情",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="租户不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_tenant(
    request: Request,
    tenant_uuid: UUID,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_data = tenant_service.get_tenant_detail(tenant_uuid)
    return success(data=tenant_data)


@router.delete(
    "/{tenant_uuid}",
    summary="删除租户",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="租户不存在"
        ),
    },
)
@apply_rate_limit("10/minute")
def delete_tenant(
    request: Request,
    tenant_uuid: UUID,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_service.delete_tenant(tenant_uuid)
    return success(msg="租户删除成功")