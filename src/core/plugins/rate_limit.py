"""
限流插件模块

提供统一的接口限流功能，基于 slowapi 实现。
"""

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)


def apply_rate_limit(rate: str = "5/minute"):
    """
    限流装饰器工厂函数

    Args:
        rate: 限流速率，格式为 "数量/时间单位"
              例如: "5/minute", "10/second", "100/hour"

    Returns:
        限流装饰器，测试环境下直接返回原函数
    """
    if os.getenv("TESTING", "false").lower() == "true":
        return lambda func: func
    return limiter.limit(rate)
