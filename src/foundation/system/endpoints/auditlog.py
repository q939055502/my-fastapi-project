from datetime import datetime

from fastapi import APIRouter, Query, Request
from src.core.plugins import apply_rate_limit
from src.core.response import success_page
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.system.service.audit_log_service import audit_log_service

router = APIRouter(
    tags=["平台管理-审计日志"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get("/list", summary="获取操作日志列表")
@apply_rate_limit("30/minute")
def get_audit_log_list(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    username: str = Query("", description="操作人名称"),
    module: str = Query("", description="功能模块"),
    method: str = Query("", description="请求方法"),
    summary: str = Query("", description="接口描述"),
    status: int = Query(None, description="状态码"),
    start_time: datetime = Query(None, description="开始时间"),
    end_time: datetime = Query(None, description="结束时间"),
):
    total, data = audit_log_service.get_list(
        page=page,
        page_size=page_size,
        username=username,
        module=module,
        method=method,
        summary=summary,
        status=status,
        start_time=start_time,
        end_time=end_time,
    )
    return success_page(data=data, total=total, page=page, page_size=page_size)