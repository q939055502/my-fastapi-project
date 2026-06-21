"""
FastAPI应用配置模块

本模块包含FastAPI应用创建时的配置函数：
- 中间件配置
- 异常处理注册
- 路由注册
- SQLAlchemy 事件监听器注册

src/__init__.py create_app() 调用
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError

from src.core.config import settings
from src.core.exceptions import (
    BusinessException,
    BusinessExceptionHandle,
    GlobalExceptionHandle,
    HttpExcHandle,
    IntegrityHandle,
    JWTErrorHandle,
    RateLimitExceededHandle,
    RequestValidationHandle,
    ResponseValidationHandle,
)
from src.core.middlewares import (
    BackGroundTaskMiddleware,
    SecurityHeadersMiddleware,
)
from src.core.plugins import limiter
from src.foundation.iam import auth_middleware, data_permission  # noqa: F401
from src.foundation.middlewares import (
    HttpAuditLogMiddleware,
    RequestContextMiddleware,
    RequestLogMiddleware,
)


def make_middlewares():
    """
    配置FastAPI中间件列表

    中间件执行顺序(从外到内):
    1. CORS - 跨域资源共享
    2. SecurityHeaders - 安全响应头
    3. RequestContext - 请求上下文管理
    4. RequestLog - 请求日志记录
    5. Auth - 权限校验
    6. BackGroundTask - 后台任务处理
    7. HttpAuditLog - HTTP 审计日志
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
        Middleware(RequestLogMiddleware),
        Middleware(auth_middleware),
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
    注册全局异常处理

    将自定义异常处理类注册到FastAPI应用中，
    使其在对应的异常抛出时被自动调用。
    """
    import jwt
    from fastapi import HTTPException

    app.add_exception_handler(BusinessException, BusinessExceptionHandle)
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
    注册API路由

    将所有API路由注册到应用,并添加统一前缀。
    """
    from src.api import api_router

    app.include_router(api_router, prefix=prefix)
