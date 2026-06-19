"""
��̨���������Ĺ���ģ��

�����������������д��ݺ�̨�������
"""

from contextvars import ContextVarfrom starlette.background import BackgroundTasks# ��̨���������ı������洢��ǰ����ĺ�̨�������
CTX_BG_TASKS: ContextVar[BackgroundTasks | None] = ContextVar("bg_tasks", default=None)


def get_bg_tasks() -> BackgroundTasks | None:
    """��ȡ��ǰ����ĺ�̨�������"""
    return CTX_BG_TASKS.get()


def set_bg_tasks(bg_tasks: BackgroundTasks) -> None:
    """���õ�ǰ����ĺ�̨�������"""
    CTX_BG_TASKS.set(bg_tasks)


def clear_bg_tasks() -> None:
    """��պ�̨����������"""
    CTX_BG_TASKS.set(None)
