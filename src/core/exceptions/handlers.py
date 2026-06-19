"""
异常处理器模块

定义全局异常处理函数，将异常转换为统一响应格式。
"""

import jwt
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse, Response
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from src.core.config import settings
from src.core.exceptions.business import BusinessException
from src.core.response import RESPONSE_MSG, error_response


def BusinessExceptionHandle(request: Request, exc: BusinessException) -> JSONResponse:
    """处理业务异常"""
    msg = exc.msg or RESPONSE_MSG.get(exc.code, "系统错误")
    return error_response(
        code=exc.code,
        msg=msg,
        detail=exc.detail,
        request_id=getattr(request.state, "request_id", None)
    )


def HttpExcHandle(request: Request, exc: HTTPException) -> JSONResponse | Response:
    """处理HTTP异常"""
    # 对于文档页面，返回 HTML 401 响应以触发浏览器登录弹窗
    if exc.status_code == 401 and request.url.path in ("/docs", "/redoc", "/openapi.json"):
        from fastapi.responses import HTMLResponse
        return HTMLResponse(
            status_code=401,
            content="Unauthorized",
            headers={"WWW-Authenticate": "Basic realm=\"Swagger UI\""},
        )
    if exc.status_code == 401:
        return error_response(
            code=40100,
            msg=RESPONSE_MSG.get(40100, "未授权"),
            detail=exc.detail if settings.DEBUG else None,
            request_id=getattr(request.state, "request_id", None)
        )
    elif exc.status_code == 403:
        return error_response(
            code=40300,
            msg=RESPONSE_MSG.get(40300, "禁止访问"),
            detail=exc.detail if settings.DEBUG else None,
            request_id=getattr(request.state, "request_id", None)
        )
    elif exc.status_code == 404:
        return error_response(
            code=40401,
            msg=RESPONSE_MSG.get(40401, "资源不存在"),
            detail=exc.detail if settings.DEBUG else None,
            request_id=getattr(request.state, "request_id", None)
        )
    elif exc.status_code == 422:
        return error_response(
            code=42200,
            msg=RESPONSE_MSG.get(42200, "参数验证失败"),
            detail=exc.detail if settings.DEBUG else None,
            request_id=getattr(request.state, "request_id", None)
        )
    else:
        return error_response(
            code=50000,
            msg=RESPONSE_MSG.get(50000, "系统错误"),
            detail=exc.detail if settings.DEBUG else None,
            request_id=getattr(request.state, "request_id", None)
        )


def IntegrityHandle(request: Request, exc: IntegrityError) -> JSONResponse:
    """处理数据完整性异常"""
    detail = f"IntegrityError: {exc}" if settings.DEBUG else None
    return error_response(
        code=50000,
        msg=RESPONSE_MSG.get(50000, "系统错误"),
        detail=detail,
        request_id=getattr(request.state, "request_id", None)
    )


def RequestValidationHandle(_: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求验证异常"""
    detail = str(exc.errors()) if settings.DEBUG else None
    return error_response(
        code=42200,
        msg=RESPONSE_MSG.get(42200, "参数验证失败"),
        detail=detail
    )


def ResponseValidationHandle(_: Request, exc: ResponseValidationError) -> JSONResponse:
    """处理响应验证异常"""
    detail = f"ResponseValidationError: {exc}" if settings.DEBUG else None
    return error_response(
        code=50000,
        msg=RESPONSE_MSG.get(50000, "系统错误"),
        detail=detail
    )


def JWTErrorHandle(request: Request, exc: jwt.InvalidTokenError) -> JSONResponse:
    """处理JWT令牌错误"""
    return error_response(
        code=40101,
        msg=RESPONSE_MSG.get(40101, "令牌格式错误"),
        request_id=getattr(request.state, "request_id", None)
    )


def RateLimitExceededHandle(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """处理限流异常"""
    response = error_response(
        code=42900,
        msg=RESPONSE_MSG.get(42900, "请求过于频繁"),
        detail={"suggestion": "请等待一段时间后再试"},
        request_id=getattr(request.state, "request_id", None)
    )
    if hasattr(exc, 'headers') and exc.headers:
        response.headers.update(exc.headers)
    return response


def GlobalExceptionHandle(request: Request, exc: Exception) -> JSONResponse:
    """全局兜底异常处理"""
    detail = f"Unexpected error: {exc}" if settings.DEBUG else None
    return error_response(
        code=50000,
        msg=RESPONSE_MSG.get(50000, "系统错误"),
        detail=detail,
        request_id=getattr(request.state, "request_id", None)
    )
