"""
异常模块

包含异常定义和异常处理器。
"""

from .business import BusinessException
from .common import DoesNotExist, SettingNotFound
from .handlers import (
    BusinessExceptionHandle,
    DoesNotExistHandle,
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
    "DoesNotExist",
    "SettingNotFound",
    # 异常处理器
    "DoesNotExistHandle",
    "BusinessExceptionHandle",
    "HttpExcHandle",
    "IntegrityHandle",
    "RequestValidationHandle",
    "ResponseValidationHandle",
    "JWTErrorHandle",
    "RateLimitExceededHandle",
    "GlobalExceptionHandle",
]
