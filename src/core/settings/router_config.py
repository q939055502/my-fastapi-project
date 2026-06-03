from src.core.enums.error_code import ErrorCode
from src.core.handlers import gen_swagger_response

DEFAULT_ROUTER_RESPONSES = {
    422: gen_swagger_response(
        codes=[ErrorCode.VALIDATION_ERROR],
        description="参数校验失败"
    ),
    429: gen_swagger_response(
        codes=[ErrorCode.RATE_LIMIT_EXCEEDED, ErrorCode.ACCOUNT_RATE_LIMIT_EXCEEDED],
        description="请求过于频繁"
    ),
    500: gen_swagger_response(
        codes=[ErrorCode.SERVER_ERROR],
        description="服务器内部错误"
    ),
}
