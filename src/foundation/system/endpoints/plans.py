"""
套餐管理接口(超级管理员专用)
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from src.core.base.schema_base import PaginationResponse
from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse, gen_swagger_response
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.iam import PermissionControl
from src.foundation.system.schemas.tenant_plan import (
    TenantPlanBase,
    TenantPlanCreate,
    TenantPlanResponse,
    TenantPlanUpdate,
)
from src.foundation.system.service.tenant_plan_service import tenant_plan_service

router = APIRouter(
    tags=["平台管理-套餐"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/",
    summary="创建套餐",
    response_model=ApiResponse[TenantPlanBase],
    responses={
        400: gen_swagger_response(
            codes=[40900],
            description="套餐名称已存在"
        ),
    },
)
@apply_rate_limit("10/minute")
def create_plan(
    request: Request,
    plan_in: TenantPlanCreate,
    current_user = Depends(PermissionControl.has_permission),
) -> ApiResponse[TenantPlanResponse]:
    plan_data = tenant_plan_service.create_plan(plan_in)
    plan_response = TenantPlanResponse.model_validate(plan_data)
    return ApiResponse(code=20000, data=plan_response, msg="套餐创建成功")


@router.put(
    "/{plan_uuid}",
    summary="更新套餐",
    response_model=ApiResponse,
)
@apply_rate_limit("30/minute")
def update_plan(
    request: Request,
    plan_uuid: UUID,
    plan_in: TenantPlanUpdate,
    current_user = Depends(PermissionControl.has_permission),
) -> ApiResponse[None]:
    tenant_plan_service.update_plan(plan_uuid, plan_in)
    return ApiResponse(code=20000, msg="套餐更新成功")


@router.get(
    "/list",
    summary="获取套餐列表",
    response_model=ApiResponse[PaginationResponse[TenantPlanResponse]],
)
@apply_rate_limit("60/minute")
def list_plans(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="套餐名称"),
    current_user = Depends(PermissionControl.has_permission),
) -> ApiResponse[PaginationResponse[TenantPlanResponse]]:
    total, data = tenant_plan_service.get_plan_list(
        page=page,
        page_size=page_size,
        name=name,
    )
    plan_list = [TenantPlanResponse.model_validate(plan) for plan in data]
    return ApiResponse(
        code=20000,
        data=PaginationResponse(
            list=plan_list,
            pagination={"total": total, "page": page, "page_size": page_size, "total_pages": (total + page_size - 1) // page_size if page_size > 0 else 0}
        ),
        msg="操作成功"
    )


@router.get(
    "/{plan_uuid}",
    summary="获取套餐详情",
    response_model=ApiResponse[TenantPlanBase],
    responses={
        404: gen_swagger_response(
            codes=[40401],
            description="套餐不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_plan(
    request: Request,
    plan_uuid: UUID,
    current_user = Depends(PermissionControl.has_permission),
) -> ApiResponse[TenantPlanResponse]:
    plan_data = tenant_plan_service.get_plan_detail(plan_uuid)
    plan_response = TenantPlanResponse.model_validate(plan_data)
    return ApiResponse(code=20000, data=plan_response)


@router.delete(
    "/{plan_uuid}",
    summary="删除套餐",
    response_model=ApiResponse,
)
@apply_rate_limit("10/minute")
def delete_plan(
    request: Request,
    plan_uuid: UUID,
    current_user = Depends(PermissionControl.has_permission),
) -> ApiResponse[None]:
    tenant_plan_service.delete_plan(plan_uuid)
    return ApiResponse(code=20000, msg="套餐删除成功")
