
"""
APScheduler 定时任务调度器模块

负责：
- 调度器的启动和停止
- 任务的注册和管理
- 与 FastAPI 应用集成
"""
from __future__ import annotations

from collections.abc import Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from src.common.core.config import settings
from src.common.core.log import logger
from src.common.core.scheduler.tasks import clean_old_logs, clean_soft_deleted_data


class SchedulerManager:
    """调度器管理器"""

    _instance: SchedulerManager | None = None
    _scheduler: BackgroundScheduler | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._scheduler is None:
            self._scheduler = BackgroundScheduler()

    def start(self):
        """启动调度器"""
        if not settings.SCHEDULER_ENABLED:
            logger.info("调度器已禁用，跳过启动")
            return

        if self._scheduler.running:
            logger.warning("调度器已在运行")
            return

        self._register_tasks()
        self._scheduler.start()
        logger.info("调度器已启动")

    def shutdown(self, wait: bool = True):
        """停止调度器

        Args:
            wait: 是否等待所有任务完成
        """
        if not self._scheduler or not self._scheduler.running:
            return

        self._scheduler.shutdown(wait=wait)
        logger.info("调度器已停止")

    def _register_tasks(self):
        """注册定时任务"""
        # 清理过期日志任务
        self._scheduler.add_job(
            func=clean_old_logs,
            trigger=CronTrigger.from_crontab(settings.SCHEDULER_CLEAN_LOG_CRON),
            id="clean_old_logs",
            name="清理过期日志",
            replace_existing=True,
        )
        logger.info(f"已注册任务：清理过期日志（Cron: {settings.SCHEDULER_CLEAN_LOG_CRON}）")

        # 清理软删除数据任务
        self._scheduler.add_job(
            func=clean_soft_deleted_data,
            trigger=CronTrigger.from_crontab(settings.SCHEDULER_CLEAN_SOFT_DELETE_CRON),
            id="clean_soft_deleted_data",
            name="清理软删除数据",
            replace_existing=True,
        )
        logger.info(f"已注册任务：清理软删除数据（Cron: {settings.SCHEDULER_CLEAN_SOFT_DELETE_CRON}）")

    def add_job(
        self,
        func: Callable,
        trigger: str,
        job_id: str,
        name: str | None = None,
        **kwargs
    ):
        """添加任务

        Args:
            func: 任务函数
            trigger: 触发器类型（cron/date/interval）
            job_id: 任务ID
            name: 任务名称
            **kwargs: 其他参数
        """
        if not self._scheduler:
            raise RuntimeError("调度器未初始化")

        self._scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            name=name,
            replace_existing=True,
            **kwargs
        )

    def remove_job(self, job_id: str):
        """移除任务

        Args:
            job_id: 任务ID
        """
        if not self._scheduler:
            return
        try:
            self._scheduler.remove_job(job_id)
            logger.info(f"已移除任务: {job_id}")
        except Exception as e:
            logger.warning(f"移除任务失败: {job_id}, 错误: {e}")


# 单例实例
scheduler_manager = SchedulerManager()

