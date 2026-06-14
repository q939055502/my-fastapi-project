
"""
定时任务实现模块

包含所有定时任务的具体实现
"""
from datetime import datetime, timedelta

from sqlalchemy import delete
from src.common.core.config import settings
from src.common.core.log import logger
from src.common.core.storage import get_db
from src.models.platform import (
    AccountBind,
    Dept,
    DictData,
    DictType,
    LoginLog,
    OperationLog,
    Permission,
    Role,
    User,
)
from src.models.platform import TenantPlan
from src.models.tenant import Tenant, TenantMember


def clean_old_logs():
    """清理过期日志任务

    清理超过保留期的登录日志和操作日志
    """
    logger.info("开始执行清理过期日志任务")
    try:
        for session in get_db():
            try:
                now = datetime.now()

                # 清理登录日志
                login_cutoff = now - timedelta(days=settings.SCHEDULER_LOGIN_LOG_RETENTION_DAYS)
                login_delete_stmt = delete(LoginLog).where(LoginLog.created_at < login_cutoff)
                login_result = session.execute(login_delete_stmt)
                login_deleted = login_result.rowcount

                # 清理操作日志
                operation_cutoff = now - timedelta(days=settings.SCHEDULER_OPERATION_LOG_RETENTION_DAYS)
                operation_delete_stmt = delete(OperationLog).where(OperationLog.created_at < operation_cutoff)
                operation_result = session.execute(operation_delete_stmt)
                operation_deleted = operation_result.rowcount

                session.commit()
                logger.info(
                    f"清理过期日志任务完成！登录日志删除: {login_deleted} 条，操作日志删除: {operation_deleted} 条"
                )
                break
            except Exception as e:
                session.rollback()
                logger.error(f"清理过期日志任务失败: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"清理过期日志任务执行异常: {str(e)}")


def clean_soft_deleted_data():
    """清理软删除数据任务

    清理超过保留期的软删除数据
    """
    logger.info("开始执行清理软删除数据任务")
    try:
        for session in get_db():
            try:
                now = datetime.now()
                cutoff = now - timedelta(days=settings.SCHEDULER_SOFT_DELETE_RETENTION_DAYS)
                total_deleted = 0

                soft_delete_models = [
                    User,
                    Role,
                    Dept,
                    Permission,
                    AccountBind,
                    DictType,
                    DictData,
                    Tenant,
                    TenantPlan,
                    TenantMember,
                ]

                for model in soft_delete_models:
                    if not hasattr(model, "delete_time"):
                        continue

                    delete_stmt = delete(model).where(
                        model.delete_time.isnot(None),
                        model.delete_time < cutoff
                    )
                    result = session.execute(delete_stmt)
                    deleted = result.rowcount
                    total_deleted += deleted

                    if deleted > 0:
                        logger.info(f"{model.__tablename__} 删除了 {deleted} 条软删除数据")

                session.commit()
                logger.info(f"清理软删除数据任务完成！共删除: {total_deleted} 条")
                break
            except Exception as e:
                session.rollback()
                logger.error(f"清理软删除数据任务失败: {str(e)}")
                raise
    except Exception as e:
        logger.error(f"清理软删除数据任务执行异常: {str(e)}")

