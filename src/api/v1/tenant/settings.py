"""
租户配置接口（超级管理员/租户管理员）
"""

from fastapi import APIRouter, Depends, Request

from src.core.auth import PermissionControl
from src.core.enums.response_code import ResponseCode
from src.core.handlers import success
from src.core.handlers.response import gen_swagger_response
from src.core.plugins import apply_rate_limit
from src.core.settings.router_config import DEFAULT_ROUTER_RESPONSES

router = APIRouter(
    tags=["租户管理-设置"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.put(
    "/{tenant_id}/config",
    summary="更新租户配置",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="租户不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_tenant_config(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(msg="租户配置更新成功")


@router.put(
    "/{tenant_id}/quota",
    summary="更新租户配额",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="租户不存在"
        ),
    },
)
@apply_rate_limit("10/minute")
def update_tenant_quota(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(msg="租户配额更新成功")


@router.get(
    "/{tenant_id}/config",
    summary="获取租户配置",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="租户不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_tenant_config(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(data={})


@router.get(
    "/{tenant_id}/quota",
    summary="获取租户配额",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="租户不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_tenant_quota(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(data={})
