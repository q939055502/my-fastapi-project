"""
租户配置接口（超级管理员/租户管理员）
"""

from fastapi import APIRouter, Depends, Request

from src.core.response import success
from src.core.dependency import PermissionControl
from src.core.rate_limit import apply_rate_limit


router = APIRouter()


@router.get("/{tenant_id}/config", summary="获取租户配置")
@apply_rate_limit("60/minute")
def get_tenant_config(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(data={})


@router.put("/{tenant_id}/config", summary="更新租户配置")
@apply_rate_limit("30/minute")
def update_tenant_config(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(msg="租户配置更新成功")


@router.get("/{tenant_id}/quota", summary="获取租户配额")
@apply_rate_limit("60/minute")
def get_tenant_quota(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(data={})


@router.put("/{tenant_id}/quota", summary="更新租户配额")
@apply_rate_limit("10/minute")
def update_tenant_quota(
    request: Request,
    tenant_id: int,
    current_user = Depends(PermissionControl.has_permission),
):
    return success(msg="租户配额更新成功")