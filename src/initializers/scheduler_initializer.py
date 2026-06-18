"""
定时任务初始化器

负责系统定时任务的初始化配置

职责：
- 注册业务定时任务
- 配置日志清理任务（访问日志、错误日志、业务日志等）
- 配置软删除数据清理任务
- 设置任务执行时间（Cron表达式）

幂等性保证：
- 检查是否已存在定时任务配置，若存在则跳过创建
- 重复执行不会产生重复数据
"""

from datetime import datetime, timedelta

from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import delete
from src.core.config import settings
from src.core.log import logger
from src.core.scheduler import scheduler_manager
from src.core.storage import get_db
from src.models.platform import (
    AccountBind,
    DictData,
    DictType,
    LoginLog,
    OperationLog,
    Org,
    Permission,
    Role,
    TenantPlan,
    User,
)
from src.models.tenant import Member, Tenant


def clean_old_logs():
    """清理过期日志任务

    清理超过保留期的登录日志和操作日志
    """
    logger.info("开始执行清理过期日志任务")
    try:
        for session in get_db():
            try:
                now = datetime.now()

                login_cutoff = now - timedelta(days=settings.SCHEDULER_LOGIN_LOG_RETENTION_DAYS)
                login_delete_stmt = delete(LoginLog).where(LoginLog.created_at < login_cutoff)
                login_result = session.execute(login_delete_stmt)
                login_deleted = login_result.rowcount

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
                    Org,
                    Permission,
                    AccountBind,
                    DictType,
                    DictData,
                    Tenant,
                    TenantPlan,
                    Member,
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


def init_scheduler():
    """
    初始化系统定时任务

    注册默认定时任务：
    1. 日志清理任务 - 根据配置的Cron表达式执行
       - 清理过期的访问日志、错误日志、业务日志等
    2. 软删除数据清理任务 - 根据配置的Cron表达式执行
       - 清理超过保留期的软删除数据
    """
    if not settings.SCHEDULER_ENABLED:
        logger.info("调度器已禁用，跳过业务任务注册")
        return

    scheduler_manager.add_job(
        func=clean_old_logs,
        trigger=CronTrigger.from_crontab(settings.SCHEDULER_CLEAN_LOG_CRON),
        job_id="clean_old_logs",
        name="清理过期日志",
    )
    logger.info(f"已注册业务任务：清理过期日志（Cron: {settings.SCHEDULER_CLEAN_LOG_CRON}）")

    scheduler_manager.add_job(
        func=clean_soft_deleted_data,
        trigger=CronTrigger.from_crontab(settings.SCHEDULER_CLEAN_SOFT_DELETE_CRON),
        job_id="clean_soft_deleted_data",
        name="清理软删除数据",
    )
    logger.info(f"已注册业务任务：清理软删除数据（Cron: {settings.SCHEDULER_CLEAN_SOFT_DELETE_CRON}）")


__all__ = [
    "init_scheduler",
    "clean_old_logs",
    "clean_soft_deleted_data",
]