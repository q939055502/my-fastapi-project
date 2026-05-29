"""
异常处理模块

定义全局异常处理函数。
"""

import jwt
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from src.core.config import settings
from src.core.constants import (
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NOT_FOUND,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_UNAUTHORIZED,
    HTTP_UNPROCESSABLE_ENTITY,
)
from src.core.handlers.response import fail


class DoesNotExist(Exception):
    """资源不存在异常"""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message)
        self.message = message


class SettingNotFound(Exception):
    """设置不存在异常"""
    def __init__(self, key: str = None):
        message = f"Setting '{key}' not found" if key else "Setting not found"
        super().__init__(message)
        self.key = key
        self.message = message


def DoesNotExistHandle(req: Request, exc: DoesNotExist) -> JSONResponse:
    """处理资源不存在异常"""
    msg = f"Object not found: {exc}, query_params: {req.query_params}" if settings.DEBUG else "请求的资源不存在"
    return fail(msg=msg, code=HTTP_NOT_FOUND)


def HttpExcHandle(request: Request, exc: HTTPException) -> JSONResponse:
    """处理HTTP异常"""
    if exc.status_code == 401 and exc.headers and "WWW-Authenticate" in exc.headers:
        response = fail(msg=exc.detail, code=exc.status_code)
        response.headers.update(exc.headers)
        return response
    return fail(msg=exc.detail, code=exc.status_code)


def IntegrityHandle(request: Request, exc: IntegrityError) -> JSONResponse:
    """处理数据完整性异常"""
    msg = f"IntegrityError: {exc}" if settings.DEBUG else "数据完整性错误，请检查输入数据"
    return fail(msg=msg, code=HTTP_INTERNAL_SERVER_ERROR)


def RequestValidationHandle(_: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求验证异常"""
    msg = f"RequestValidationError: {exc}" if settings.DEBUG else "请求参数验证失败，请检查输入格式"
    return fail(msg=msg, code=HTTP_UNPROCESSABLE_ENTITY)


def ResponseValidationHandle(_: Request, exc: ResponseValidationError) -> JSONResponse:
    """处理响应验证异常"""
    msg = f"ResponseValidationError: {exc}" if settings.DEBUG else "服务器响应格式错误"
    return fail(msg=msg, code=HTTP_INTERNAL_SERVER_ERROR)


def JWTErrorHandle(request: Request, exc: jwt.InvalidTokenError) -> JSONResponse:
    """处理JWT令牌错误"""
    return fail(msg="无效的Token", code=HTTP_UNAUTHORIZED)


def RateLimitExceededHandle(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """处理限流异常"""
    response = fail(
        msg="请求过于频繁，请稍后重试",
        code=HTTP_TOO_MANY_REQUESTS,
        detail={"suggestion": "请等待一段时间后再试"}
    )
    if hasattr(exc, 'headers') and exc.headers:
        response.headers.update(exc.headers)
    return response


def GlobalExceptionHandle(request: Request, exc: Exception) -> JSONResponse:
    """全局兜底异常处理"""
    msg = f"Unexpected error: {exc}" if settings.DEBUG else "服务器响应格式错误"
    return fail(msg=msg, code=HTTP_INTERNAL_SERVER_ERROR)
