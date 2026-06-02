"""Audit Log Service"""

from datetime import datetime

from sqlalchemy import func, select

from src.core.storage import TransactionManager
from src.models.system import AuditLog


class AuditLogService:
    """Service for audit log operations"""

    def get_list(
        self,
        page: int = 1,
        page_size: int = 10,
        username: str = "",
        module: str = "",
        method: str = "",
        summary: str = "",
        status: int = None,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> tuple[int, list[dict]]:
        """Get audit log list with filters"""
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

        with TransactionManager() as tm:
            count_query = select(func.count()).select_from(AuditLog)
            for filter_condition in filters:
                count_query = count_query.where(filter_condition)
            count_result = tm.session.execute(count_query)
            total = count_result.scalar()

            query = select(AuditLog)
            for filter_condition in filters:
                query = query.where(filter_condition)
            offset = (page - 1) * page_size
            query = query.offset(offset).limit(page_size).order_by(AuditLog.created_at.desc())
            result = tm.session.execute(query)
            audit_log_objs = result.scalars().all()

            data = [audit_log.to_dict() for audit_log in audit_log_objs]
            return total, data


audit_log_service = AuditLogService()
