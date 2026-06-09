"""
Core 模块

系统核心模块，包含：
- auth: 认证模块（密码、JWT、令牌、权限）
- middlewares: HTTP中间件
- handlers: 业务处理器
- plugins: 插件（限流等）
- storage: 存储层
- log: 日志
- config: 配置
- constants: 常量
"""

# 导出主要模块方便导入
from . import auth, config, constants, handlers, log, middlewares, plugins, storage

__all__ = [
    "auth",
    "middlewares",
    "handlers",
    "plugins",
    "storage",
    "log",
    "config",
    "constants",
]
