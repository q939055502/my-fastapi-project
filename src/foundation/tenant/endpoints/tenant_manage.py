"""
平台管理租户接口(超级管理员专用)
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field
from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse, swagger_responses
from src.foundation.iam import require_auth, require_permission
from src.foundation.tenant.schemas.tenant import (
    TenantCreate,
    TenantResponse,
    TenantUpdate,
)
from src.foundation.tenant.service.tenant_service import tenant_service

router = APIRouter(
    tags=["平台管理-租户"],
)


class TenantListResponse(BaseModel):
    """租户列表响应"""
    list: Annotated[list[TenantResponse], Field(..., description="租户列表")]
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


@router.post(
    "/",
    summary="创建租户",
    dependencies=[require_auth, require_permission("tenant:create")],
    responses=swagger_responses(
        codes=[40900],
        success_msg="租户名称已存在",
    ),
)
@apply_rate_limit("10/minute")
def create_tenant(
    request: Request,
    tenant_in: TenantCreate,
) -> ApiResponse[TenantResponse]:
    tenant = tenant_service.create_tenant(tenant_in)
    tenant_response = TenantResponse.model_validate(tenant)
    return ApiResponse(code=20000, msg="租户创建成功", data=tenant_response)


@router.put(
    "/{tenant_uuid}",
    summary="更新租户",
    dependencies=[require_auth, require_permission("tenant:update")],
)
@apply_rate_limit("30/minute")
def update_tenant(
    request: Request,
    tenant_uuid: UUID,
    tenant_in: TenantUpdate,
) -> ApiResponse[None]:
    tenant_service.update_tenant(str(tenant_uuid), tenant_in)
    return ApiResponse(code=20000, msg="租户更新成功")


@router.get("/list", summary="获取租户列表", dependencies=[require_auth, require_permission("tenant:list")])
@apply_rate_limit("60/minute")
def list_tenants(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="租户名称"),
    status: bool = Query(None, description="状态"),
) -> ApiResponse[TenantListResponse]:
    total, tenants = tenant_service.get_tenant_list(
        page=page,
        page_size=page_size,
        name=name,
        status=status,
    )
    tenant_responses = [TenantResponse.model_validate(t) for t in tenants]
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ApiResponse(
        code=20000,
        msg="操作成功",
        data=TenantListResponse(
            list=tenant_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get(
    "/{tenant_uuid}",
    summary="获取租户详情",
    dependencies=[require_auth, require_permission("tenant:read")],
)
@apply_rate_limit("60/minute")
def get_tenant(
    request: Request,
    tenant_uuid: UUID,
) -> ApiResponse[TenantResponse]:
    tenant = tenant_service.get_tenant_detail(str(tenant_uuid))
    tenant_response = TenantResponse.model_validate(tenant)
    return ApiResponse(code=20000, msg="操作成功", data=tenant_response)


@router.delete(
    "/{tenant_uuid}",
    summary="删除租户",
    dependencies=[require_auth, require_permission("tenant:delete")],
)
@apply_rate_limit("10/minute")
def delete_tenant(
    request: Request,
    tenant_uuid: UUID,
) -> ApiResponse[None]:
    tenant_service.delete_tenant(str(tenant_uuid))
    return ApiResponse(code=20000, msg="租户删除成功")
