"""
响应配置模块

包含响应消息, 响应模型和路由响应配置
"""

from .openapi_custom import gen_swagger_response, swagger_responses
from .response_model import (
    ApiResponse,
    PaginationResponse,
    error_response,
    success,
    success_page,
)
from .response_msg import RESPONSE_MSG, load_response_msg

__all__ = [
    # 响应模型
    "ApiResponse",
    "PaginationResponse",
    # 响应工具函数
    "success",
    "success_page",
    "error_response",
    # OpenAPI 响应配置
    "swagger_responses",
    "gen_swagger_response",
    # 响应消息
    "RESPONSE_MSG",
    "load_response_msg",
]
