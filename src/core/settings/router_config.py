from src.core.enums.response_code import ResponseCode
from src.core.handlers import gen_swagger_response

DEFAULT_ROUTER_RESPONSES = {
    422: gen_swagger_response(
        codes=[ResponseCode.VALIDATION_ERROR],
        description="参数校验失败"
    ),
    429: gen_swagger_response(
        codes=[ResponseCode.RATE_LIMIT_EXCEEDED, ResponseCode.ACCOUNT_RATE_LIMIT_EXCEEDED],
        description="请求过于频繁"
    ),
    500: gen_swagger_response(
        codes=[ResponseCode.SERVER_ERROR],
        description="服务器内部错误"
    ),
}
