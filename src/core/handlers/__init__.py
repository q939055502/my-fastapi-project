"""
处理器模块

包含各种业务处理器：
- exceptions: 异常处理
- response: 响应格式
- validator: 验证器
- init_app: 数据初始化
- bgtask: 后台任务
"""

from .bgtask import BgTasks
from .exceptions import (
    DoesNotExist,
    DoesNotExistHandle,
    GlobalExceptionHandle,
    HttpExcHandle,
    IntegrityHandle,
    JWTErrorHandle,
    RateLimitExceededHandle,
    RequestValidationHandle,
    ResponseValidationHandle,
    SettingNotFound,
)
from .init_app import init_data
from .response import (
    ApiResponse,
    fail,
    success,
    success_page,
)
from .validator import (
    GlobalValidator,
    validate_email,
    validate_id_card,
    validate_phone,
)

__all__ = [
    # exceptions
    "DoesNotExist",
    "SettingNotFound",
    "DoesNotExistHandle",
    "HttpExcHandle",
    "IntegrityHandle",
    "RequestValidationHandle",
    "ResponseValidationHandle",
    "JWTErrorHandle",
    "RateLimitExceededHandle",
    "GlobalExceptionHandle",
    # response
    "ApiResponse",
    "success",
    "success_page",
    "fail",
    # validator
    "validate_phone",
    "validate_email",
    "validate_id_card",
    "GlobalValidator",
    # bgtask
    "BgTasks",
    # init
    "init_data",
]
