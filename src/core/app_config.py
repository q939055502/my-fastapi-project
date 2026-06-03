
"""
应用配置模块

本模块包含 FastAPI 应用创建时的配置函数
- 中间件配置
- 异常处理注册
- 路由注册

在 src/__init__.py 中 create_app() 调用
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from src.core.config import settings
from src.core.handlers import (
    BusinessException,
    BusinessExceptionHandle,
    DoesNotExist,
    DoesNotExistHandle,
    GlobalExceptionHandle,
    HttpExcHandle,
    IntegrityHandle,
    RateLimitExceededHandle,
    RequestValidationHandle,
    ResponseValidationHandle,
)
from src.core.middlewares import (
    BackGroundTaskMiddleware,
    HttpAuditLogMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)
from src.core.plugins import limiter


def make_middlewares():
    """
    配置 FastAPI 中间件列表

    中间件执行顺序（从外到内）：
    1. CORS - 跨域资源共享
    2. SecurityHeaders - 安全响应头
    3. RequestContext - 请求上下文管理（包含请求日志记录）
    4. BackGroundTask - 后台任务处理
    5. HttpAuditLog - HTTP 审计日志
    """
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=settings.CORS_ORIGINS_LIST,
            allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
            allow_methods=settings.CORS_ALLOW_METHODS,
            allow_headers=settings.CORS_ALLOW_HEADERS,
        ),
        Middleware(SecurityHeadersMiddleware),
        Middleware(RequestContextMiddleware),
        Middleware(BackGroundTaskMiddleware),
        Middleware(
            HttpAuditLogMiddleware,
            methods=["GET", "POST", "PUT", "DELETE"],
            exclude_paths=[
                "/api/v1/auth/login",
                "/docs",
                "/openapi.json",
                "/favicon.ico",
            ],
        ),
    ]
    return middleware


def register_exceptions(app: FastAPI):
    """
    注册全局异常处理器

    将自定义异常处理类注册到 FastAPI 应用中
    使其在对应的异常抛出时被自动调用
    """
    import jwt
    from fastapi import HTTPException

    from src.core.handlers import JWTErrorHandle

    app.add_exception_handler(BusinessException, BusinessExceptionHandle)
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)
    app.add_exception_handler(jwt.InvalidTokenError, JWTErrorHandle)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, RateLimitExceededHandle)
    app.add_exception_handler(Exception, GlobalExceptionHandle)


def register_routers(app: FastAPI, prefix: str = "/api"):
    """
    注册 API 路由

    将所有 API 路由注册到应用，并添加统一前缀
    """
    from src.api import api_router
    app.include_router(api_router, prefix=prefix)

