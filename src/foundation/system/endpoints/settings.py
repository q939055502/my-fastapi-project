"""
平台全局设置接口(超级管理员专用�?"""

from fastapi import APIRouter, Depends, Request

from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.iam import PermissionControl
from src.foundation.system.schemas.system_config import SystemConfigUpdate
from src.foundation.system.service.system_config_service import system_config_service

router = APIRouter(
    tags=["平台管理-设置"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.put("/", summary="更新平台全局设置")
@apply_rate_limit("30/minute")
def update_settings(
    request: Request,
    config_update: SystemConfigUpdate,
    current_user = Depends(PermissionControl.has_permission),
) -> ApiResponse[None]:
    system_config_service.update_configs(config_update)
    return ApiResponse(code=20000, msg="设置更新成功")


@router.get("/", summary="获取平台全局设置")
@apply_rate_limit("60/minute")
def get_settings(request: Request, current_user = Depends(PermissionControl.has_permission)) -> ApiResponse[dict]:
    configs = system_config_service.get_all_configs()
    return ApiResponse(code=20000, data=configs)
