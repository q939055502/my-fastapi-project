"""
租户管理接口（超级管理员专用）
"""

from fastapi import APIRouter, Depends, Query, Request
from src.common.core.auth import PermissionControl
from src.common.core.enums.response_code import ResponseCode
from src.common.core.plugins import apply_rate_limit
from src.common.core.response import gen_swagger_response, success, success_page
from src.common.core.response.router_config import DEFAULT_ROUTER_RESPONSES

router = APIRouter(
    tags=["租户管理-管理"],
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
def create_tenant(request: Request, current_user = Depends(PermissionControl.has_permission)):
    return success(msg="租户创建成功")


@router.put(
    "/{tenant_id}",
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
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(msg="租户更新成功")


@router.get("/", summary="获取租户列表")
@apply_rate_limit("60/minute")
def list_tenants(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="租户名称"),
    status: int = Query(None, description="状态"),
    current_user = Depends(PermissionControl.has_permission),
):
    return success_page(data=[], total=0, page=page, page_size=page_size)


@router.get(
    "/{tenant_id}",
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
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(data={})


@router.delete(
    "/{tenant_id}",
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
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(msg="租户删除成功")
