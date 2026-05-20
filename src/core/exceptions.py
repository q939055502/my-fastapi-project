
from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.responses import Response
from sqlalchemy.exc import IntegrityError
from slowapi.errors import RateLimitExceeded
import jwt

from src.core.config import settings


class DoesNotExist(Exception):
    pass


class SettingNotFound(Exception):
    pass


def DoesNotExistHandle(req: Request, exc: DoesNotExist) -> JSONResponse:
    if settings.DEBUG:
        msg = f"Object not found: {exc}, query_params: {req.query_params}"
    else:
        msg = "请求的资源不存在"

    content = dict(code=404, msg=msg)
    return JSONResponse(content=content, status_code=404)


def HttpExcHandle(request: Request, exc: HTTPException):
    if exc.status_code == 401 and exc.headers and "WWW-Authenticate" in exc.headers:
        return Response(status_code=exc.status_code, headers=exc.headers)
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "msg": exc.detail, "data": None},
        media_type="application/json; charset=utf-8"
    )


def IntegrityHandle(request: Request, exc: IntegrityError):
    if settings.DEBUG:
        msg = f"IntegrityError: {exc}"
    else:
        msg = "数据完整性错误，请检查输入数据"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=500)


def RequestValidationHandle(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    if settings.DEBUG:
        msg = f"RequestValidationError: {exc}"
    else:
        msg = "请求参数验证失败，请检查输入格式"

    content = dict(code=422, msg=msg)
    return JSONResponse(content=content, status_code=422)


def ResponseValidationHandle(
    _: Request, exc: ResponseValidationError
) -> JSONResponse:
    if settings.DEBUG:
        msg = f"ResponseValidationError: {exc}"
    else:
        msg = "服务器响应格式错误"

    content = dict(code=500, msg=msg)
    return JSONResponse(content=content, status_code=500)


def JWTErrorHandle(request: Request, exc: jwt.InvalidTokenError) -> JSONResponse:
    """处理JWT令牌错误"""
    return JSONResponse(
        status_code=401,
        content={"code": 401, "msg": "令牌无效或已过期", "data": None},
        media_type="application/json; charset=utf-8"
    )


def RateLimitExceededHandle(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """处理限流异常"""
    headers = {}
    
    if hasattr(exc, 'headers') and exc.headers:
        headers.update(exc.headers)
    
    return JSONResponse(
        status_code=429,
        content={
            "code": 429, 
            "msg": "请求过于频繁，请稍后重试", 
            "data": None,
            "suggestion": "请等待一段时间后再试"
        },
        headers=headers,
        media_type="application/json; charset=utf-8"
    )

