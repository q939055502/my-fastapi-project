"""
插件模块

包含可插拔的功能扩展：
- rate_limit: 限流器
- (未来可扩展: cache, monitoring, tracing 等)
"""

from .rate_limit import apply_rate_limit, limiter

__all__ = [
    "limiter",
    "apply_rate_limit",
]
