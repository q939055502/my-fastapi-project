from datetime import datetime

from fastapi import APIRouter, Query, Request
from sqlalchemy import func, select

from src.core.handlers import success_page
from src.core.plugins import apply_rate_limit
from src.core.storage import UnitOfWork
from src.models.system import AuditLog

router = APIRouter(tags=["平台管理-审计日志"])


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
    filters = []
    if username:
        filters.append(AuditLog.username.contains(username))
    if module:
        filters.append(AuditLog.module.contains(module))
    if method:
        filters.append(AuditLog.method.contains(method))
    if summary:
        filters.append(AuditLog.summary.contains(summary))
    if status is not None:
        filters.append(AuditLog.status == status)
    if start_time and end_time:
        filters.append(AuditLog.created_at.between(start_time, end_time))
    elif start_time:
        filters.append(AuditLog.created_at >= start_time)
    elif end_time:
        filters.append(AuditLog.created_at <= end_time)

    with UnitOfWork() as uow:
        count_query = select(func.count()).select_from(AuditLog)
        for filter_condition in filters:
            count_query = count_query.where(filter_condition)
        count_result = uow.session.execute(count_query)
        total = count_result.scalar()

        query = select(AuditLog)
        for filter_condition in filters:
            query = query.where(filter_condition)
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size).order_by(AuditLog.created_at.desc())
        result = uow.session.execute(query)
        audit_log_objs = result.scalars().all()

        data = [audit_log.to_dict() for audit_log in audit_log_objs]
        return success_page(data=data, total=total, page=page, page_size=page_size)
