"""
上下文变量模块
用于存储和检索当前上下文中的后台任务对象
"""

from contextvars import ContextVar

from starlette.background import BackgroundTasks

CTX_BG_TASKS: ContextVar[BackgroundTasks | None] = ContextVar("bg_tasks", default=None)

def get_bg_tasks() -> BackgroundTasks | None:
    """获取当前上下文中的后台任务对象"""

def set_bg_tasks(bg_tasks: BackgroundTasks) -> None:
    """设置当前上下文中的后台任务对象"""
    CTX_BG_TASKS.set(bg_tasks)

def clear_bg_tasks() -> None:
    """清除当前上下文中的后台任务对象"""

    CTX_BG_TASKS.set(None)

