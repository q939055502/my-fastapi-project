"""
Core 模块

系统核心模块，提供基础技术能力支撑整个系统运行：
- config: 配置管理
- constants: 常量定义
- base: 基础类(Repository, Schema, 分页)
- exceptions: 异常处理与处理器
- log: 日志系统
- middlewares: HTTP中间件
- plugins: 插件(限流等)
- response: 响应统一封装
- storage: 存储层(数据库, 缓存, 文件)
- scheduler: 定时任务调度
- background_tasks: 后台任务处理
- utils: 工具函数
- validators: 参数校验器

设计原则：
1. 纯技术能力：不包含业务逻辑
2. 单向依赖：core 层不依赖 foundation 层 modules
3. 可复用：提供通用技术组件供上层调用
"""

# 导出主要模块方便导入
from . import (
    background_tasks,
    base,
    config,
    constants,
    exceptions,
    log,
    middlewares,
    plugins,
    response,
    scheduler,
    storage,
    utils,
    validators,
)
from .annotations import (
    InterfaceType,
    disable_data_permission,
    interface_type,
    login_required,
)

__all__ = [
    "base",
    "config",
    "constants",
    "exceptions",
    "log",
    "middlewares",
    "plugins",
    "response",
    "scheduler",
    "storage",
    "background_tasks",
    "utils",
    "validators",
    "InterfaceType",
    "interface_type",
    "login_required",
    "disable_data_permission",
]
