"""
后台任务上下文管理模块

用于在请求处理过程中传递后台任务对象。
"""

from contextvars import ContextVar

from starlette.background import BackgroundTasks

# 后台任务上下文变量，存储当前请求的后台任务对象
CTX_BG_TASKS: ContextVar[BackgroundTasks | None] = ContextVar("bg_tasks", default=None)


def get_bg_tasks() -> BackgroundTasks | None:
    """获取当前请求的后台任务对象"""
    return CTX_BG_TASKS.get()


def set_bg_tasks(bg_tasks: BackgroundTasks) -> None:
    """设置当前请求的后台任务对象"""
    CTX_BG_TASKS.set(bg_tasks)


def clear_bg_tasks() -> None:
    """清空后台任务上下文"""
    CTX_BG_TASKS.set(None)
