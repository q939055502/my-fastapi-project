﻿﻿﻿﻿"""
平台全局设置接口(超级管理员专用�?"""

from fastapi import APIRouter, Request
from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse
from src.foundation.iam import require_permission
from src.foundation.system.schemas.system_config import SystemConfigUpdate
from src.foundation.system.service.system_config_service import system_config_service

router = APIRouter(
    tags=["平台管理-设置"],
)


@router.put("/", summary="更新平台全局设置", dependencies=[require_permission("platform:setting:update")])
@apply_rate_limit("30/minute")
def update_settings(
    request: Request,
    config_update: SystemConfigUpdate,
) -> ApiResponse[None]:
    system_config_service.update_configs(config_update)
    return ApiResponse(code=20000, msg="设置更新成功")


@router.get("/", summary="获取平台全局设置", dependencies=[require_permission("platform:setting:read")])
@apply_rate_limit("60/minute")
def get_settings(request: Request) -> ApiResponse[dict]:
    configs = system_config_service.get_all_configs()
    return ApiResponse(code=20000, data=configs)
