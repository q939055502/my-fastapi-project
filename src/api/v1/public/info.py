"""
公开信息接口
"""

import os
from datetime import UTC, datetime

from fastapi import APIRouter, Request

from src.core.config import settings
from src.core.rate_limit import apply_rate_limit


router = APIRouter()


@router.get("/health", summary="健康检查")
@apply_rate_limit("100/minute")
def health_check(request: Request):
    """
    健康检查接口
    【类型】公开接口（无需登录）
    【权限】无需认证
    【功能】检查服务是否正常运行
    【用途】负载均衡器、健康监控平台探针
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": settings.VERSION,
        "environment": settings.APP_ENV,
        "service": "FastAPI Backend Template",
    }


@router.get("/version", summary="版本信息")
@apply_rate_limit("60/minute")
def get_version(request: Request):
    """
    版本信息接口

    【类型】公开接口（无需登录）
    【权限】无需认证
    【功能】获取服务版本信息
    【用途】前端兼容性检查、运维监控
    """
    return {
        "version": settings.VERSION,
        "app_title": settings.APP_TITLE,
        "project_name": settings.PROJECT_NAME,
        "build": os.getenv("BUILD_NUMBER", "dev"),
        "commit": os.getenv("GIT_COMMIT", "unknown"),
        "python_version": os.getenv("PYTHON_VERSION", "3.11+"),
    }