"""
后台任务模块

统一管理后台任务。
"""

from starlette.background import BackgroundTasks

from src.core.handlers.bgtask_context import CTX_BG_TASKS


class BgTasks:
    """后台任务统一管理"""

    @classmethod
    def init_bg_tasks_obj(cls):
        """实例化后台任务，并设置到上下文"""
        bg_tasks = BackgroundTasks()
        CTX_BG_TASKS.set(bg_tasks)

    @classmethod
    def get_bg_tasks_obj(cls) -> BackgroundTasks | None:
        """从上下文获取后台任务实例"""
        return CTX_BG_TASKS.get()

    @classmethod
    def add_task(cls, func, *args, **kwargs):
        """添加后台任务"""
        bg_tasks = cls.get_bg_tasks_obj()
        if bg_tasks:
            bg_tasks.add_task(func, *args, **kwargs)

    @classmethod
    def execute_tasks(cls):
        """执行后台任务，一般是请求结果返回之后执行"""
        bg_tasks = cls.get_bg_tasks_obj()
        if bg_tasks and bg_tasks.tasks:
            return bg_tasks()
