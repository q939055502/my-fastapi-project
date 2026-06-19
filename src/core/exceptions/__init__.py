"""
异常模块

包含异常定义和异常处理器.
"""

from .business import BusinessException
from .handlers import (
    BusinessExceptionHandle,
    GlobalExceptionHandle,
    HttpExcHandle,
    IntegrityHandle,
    JWTErrorHandle,
    RateLimitExceededHandle,
    RequestValidationHandle,
    ResponseValidationHandle,
)

__all__ = [
    # 异常类
    "BusinessException",
    # 异常处理器
    "BusinessExceptionHandle",
    "HttpExcHandle",
    "IntegrityHandle",
    "RequestValidationHandle",
    "ResponseValidationHandle",
    "JWTErrorHandle",
    "RateLimitExceededHandle",
    "GlobalExceptionHandle",
]
