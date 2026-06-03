"""
套餐管理接口（超级管理员专用）
"""

from fastapi import APIRouter, Depends, Query, Request

from src.core.auth import PermissionControl
from src.core.enums.error_code import ErrorCode
from src.core.handlers import success, success_page
from src.core.handlers.response import ApiResponse, gen_swagger_response
from src.core.plugins import apply_rate_limit
from src.core.settings.router_config import DEFAULT_ROUTER_RESPONSES
from src.schemas.sys.tenant_plan import (
    TenantPlanBase,
    TenantPlanCreate,
    TenantPlanUpdate,
)
from src.services.sys.tenant_plan_service import tenant_plan_service

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
            codes=[ErrorCode.DATA_ALREADY_EXIST],
            description="套餐名称已存在"
        ),
    },
)
@apply_rate_limit("10/minute")
def create_plan(
    request: Request,
    plan_in: TenantPlanCreate,
    current_user = Depends(PermissionControl.has_permission),
):
    plan_data = tenant_plan_service.create_plan(plan_in)
    return success(data=plan_data, msg="套餐创建成功")


@router.put(
    "/{plan_id}",
    summary="更新套餐",
    response_model=ApiResponse,
    responses={
        404: gen_swagger_response(
            codes=[ErrorCode.DATA_NOT_EXIST],
            description="套餐不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_plan(
    request: Request,
    plan_id: int,
    plan_in: TenantPlanUpdate,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_plan_service.update_plan(plan_id, plan_in)
    return success(msg="套餐更新成功")


@router.get(
    "/list",
    summary="获取套餐列表",
    response_model=ApiResponse[dict],
)
@apply_rate_limit("60/minute")
def list_plans(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="套餐名称"),
    current_user = Depends(PermissionControl.has_permission),
):
    total, data = tenant_plan_service.get_plan_list(
        page=page,
        page_size=page_size,
        name=name,
    )
    return success_page(data=data, total=total, page=page, page_size=page_size)


@router.get(
    "/{plan_id}",
    summary="获取套餐详情",
    response_model=ApiResponse[TenantPlanBase],
    responses={
        404: gen_swagger_response(
            codes=[ErrorCode.DATA_NOT_EXIST],
            description="套餐不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_plan(
    request: Request,
    plan_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    plan_data = tenant_plan_service.get_plan_detail(plan_id)
    return success(data=plan_data)


@router.delete(
    "/{plan_id}",
    summary="删除套餐",
    response_model=ApiResponse,
    responses={
        404: gen_swagger_response(
            codes=[ErrorCode.DATA_NOT_EXIST],
            description="套餐不存在"
        ),
    },
)
@apply_rate_limit("10/minute")
def delete_plan(
    request: Request,
    plan_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    tenant_plan_service.delete_plan(plan_id)
    return success(msg="套餐删除成功")
