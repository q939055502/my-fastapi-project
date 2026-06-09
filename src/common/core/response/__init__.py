"""
响应配置模块

包含响应消息、响应模型和路由响应配置
"""

from .response_model import (
    ApiResponse,
    PaginationInfo,
    fail,
    gen_swagger_response,
    success,
    success_page,
)
from .response_msg import RESPONSE_MSG, load_response_msg
from .router_config import DEFAULT_ROUTER_RESPONSES

__all__ = [
    # 响应模型
    "ApiResponse",
    "PaginationInfo",
    # 响应工具函数
    "success",
    "success_page",
    "fail",
    "gen_swagger_response",
    # 响应消息
    "RESPONSE_MSG",
    "load_response_msg",
    # 路由配置
    "DEFAULT_ROUTER_RESPONSES",
]
