
"""
限流工具模块

提供统一的限流功能，基于 slowapi 实现
"""

import os
from slowapi import Limiter
from slowapi.util import get_remote_address


limiter = Limiter(key_func=get_remote_address)


def apply_rate_limit(rate: str = "5/minute"):
    """
    限流装饰器工厂函数
    
    Args:
        rate: 限流速率，格式为 "数字/时间单位"
              例如: "5/minute", "10/second", "100/hour"
    
    Returns:
        装饰器函数，测试环境下会跳过限流
    """
    if os.getenv("TESTING", "false").lower() == "true":
        return lambda func: func
    return limiter.limit(rate)

