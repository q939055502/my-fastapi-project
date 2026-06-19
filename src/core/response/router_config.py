from .response_model import gen_swagger_response

DEFAULT_ROUTER_RESPONSES = {
    400: gen_swagger_response(
        codes=[40000, 40001, 40002, 40003, 40004, 40005, 40900, 40901, 40902],
        description="请求参数错误或业务条件不满足"
    ),
    401: gen_swagger_response(
        codes=[40100, 40101, 40102, 40103, 40104],
        description="未授权或登录已过期"
    ),
    403: gen_swagger_response(
        codes=[40300, 40301, 40302, 40303],
        description="无访问权限"
    ),
    404: gen_swagger_response(
        codes=[40400, 40401],
        description="资源不存在"
    ),
    422: gen_swagger_response(
        codes=[42200, 42201, 42202, 42203],
        description="参数校验失败"
    ),
    429: gen_swagger_response(
        codes=[42900, 42901],
        description="请求过于频繁"
    ),
    500: gen_swagger_response(
        codes=[50000, 50001, 50002, 50003],
        description="服务器内部错误"
    ),
}
