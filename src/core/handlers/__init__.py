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
    BusinessException,
    BusinessExceptionHandle,
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
    gen_swagger_response,
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
    "BusinessException",
    "BusinessExceptionHandle",
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
    "gen_swagger_response",
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
