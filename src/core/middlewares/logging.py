"""
请求日志中间件
"""

from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.core.auth import AuthControl
from src.core.log import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件 - 支持 tenant_id"""

    async def _get_tenant_id(self, request: Request) -> str:
        """从请求中获取租户ID"""
        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[len("Bearer "):]
                user_obj = AuthControl.authenticate_token(token, raise_exc=False)
                if user_obj and hasattr(user_obj, "tenant_id"):
                    return str(user_obj.tenant_id)
        except Exception:
            pass
        return "system"

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """处理请求并记录日志"""
        start_time = datetime.now()

        tenant_id = await self._get_tenant_id(request)
        request.state.tenant_id = tenant_id

        tenant_logger = logger.bind(tenant_id=tenant_id)

        tenant_logger.info(
            f"请求开始: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )

        try:
            response = await call_next(request)

            end_time = datetime.now()
            process_time = (end_time - start_time).total_seconds() * 1000

            tenant_logger.info(
                f"请求完成: {request.method} {request.url.path} - {response.status_code} ({process_time:.2f}ms)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "process_time_ms": process_time,
                },
            )

            return response

        except Exception as e:
            end_time = datetime.now()
            process_time = (end_time - start_time).total_seconds() * 1000

            tenant_logger.error(
                f"请求异常: {request.method} {request.url.path} - {str(e)} ({process_time:.2f}ms)",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "process_time_ms": process_time,
                },
            )

            raise
