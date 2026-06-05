"""
响应配置模块

包含响应消息和路由响应配置
"""

from .response_msg import RESPONSE_MSG, load_response_msg
from .router_config import DEFAULT_ROUTER_RESPONSES

__all__ = [
    "RESPONSE_MSG",
    "load_response_msg",
    "DEFAULT_ROUTER_RESPONSES",
]
