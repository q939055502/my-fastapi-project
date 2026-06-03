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
from src.core.enums.error_code import ErrorCode
from src.core.exceptions.exception import BusinessException
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
    detail = f"Object not found: {exc}, query_params: {req.query_params}" if settings.DEBUG else None
    return fail(code=ErrorCode.ENTITY_NOT_FOUND, detail=detail)


def BusinessExceptionHandle(request: Request, exc: BusinessException) -> JSONResponse:
    """处理业务异常"""
    return fail(exc.code, exc.detail)


def HttpExcHandle(request: Request, exc: HTTPException) -> JSONResponse:
    """处理HTTP异常"""
    if exc.status_code == 401:
        response = fail(code=ErrorCode.UNAUTHORIZED)
    elif exc.status_code == 403:
        response = fail(code=ErrorCode.FORBIDDEN)
    elif exc.status_code == 404:
        response = fail(code=ErrorCode.ENTITY_NOT_FOUND)
    elif exc.status_code == 422:
        response = fail(code=ErrorCode.VALIDATION_ERROR)
    else:
        response = fail(code=ErrorCode.SERVER_ERROR, detail=exc.detail)

    if exc.headers:
        response.headers.update(exc.headers)
    return response


def IntegrityHandle(request: Request, exc: IntegrityError) -> JSONResponse:
    """处理数据完整性异常"""
    detail = f"IntegrityError: {exc}" if settings.DEBUG else None
    return fail(code=ErrorCode.SERVER_ERROR, detail=detail)


def RequestValidationHandle(_: Request, exc: RequestValidationError) -> JSONResponse:
    """处理请求验证异常"""
    detail = str(exc.errors()) if settings.DEBUG else None
    return fail(code=ErrorCode.VALIDATION_ERROR, detail=detail)


def ResponseValidationHandle(_: Request, exc: ResponseValidationError) -> JSONResponse:
    """处理响应验证异常"""
    detail = f"ResponseValidationError: {exc}" if settings.DEBUG else None
    return fail(code=ErrorCode.SERVER_ERROR, detail=detail)


def JWTErrorHandle(request: Request, exc: jwt.InvalidTokenError) -> JSONResponse:
    """处理JWT令牌错误"""
    return fail(code=ErrorCode.TOKEN_FORMAT_INVALID)


def RateLimitExceededHandle(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """处理限流异常"""
    response = fail(
        code=ErrorCode.RATE_LIMIT_EXCEEDED,
        detail={"suggestion": "请等待一段时间后再试"}
    )
    if hasattr(exc, 'headers') and exc.headers:
        response.headers.update(exc.headers)
    return response


def GlobalExceptionHandle(request: Request, exc: Exception) -> JSONResponse:
    """全局兜底异常处理"""
    detail = f"Unexpected error: {exc}" if settings.DEBUG else None
    return fail(code=ErrorCode.SERVER_ERROR, detail=detail)
