"""
请求日志中间件

负责记录请求的开始和完成日志。
"""

from datetime import datetime

from src.foundation.iam.auth.context import get_current_auth_context
from src.core.log import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestLogMiddleware(BaseHTTPMiddleware):
    """请求日志中间件 - 记录请求的开始和完成"""

    def _create_request_logger(
        self,
        request_id: str,
        tenant_id: int | None,
        user_id: int | None,
        client_ip: str,
        path: str,
    ) -> logger:
        """创建请求日志记录器"""
        extra = {
            "request_id": request_id,
            "tenant_id": str(tenant_id) if tenant_id else "system",
            "user_id": str(user_id) if user_id else "0",
            "ip": client_ip,
            "endpoint": path,
            "duration": "0ms",
            "business_code": "-",
        }
        return logger.bind(**extra)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """处理请求并记录日志"""
        start_time = datetime.now()

        auth_ctx = get_current_auth_context()
        request_id = auth_ctx.request_id if auth_ctx else "-"
        tenant_id = auth_ctx.tenant_id if auth_ctx else None
        user_id = auth_ctx.user_id if auth_ctx else None
        client_ip = auth_ctx.client_ip if auth_ctx else "unknown"
        path = request.url.path

        request_logger = self._create_request_logger(
            request_id=request_id,
            tenant_id=tenant_id,
            user_id=user_id,
            client_ip=client_ip,
            path=path,
        )
        request_logger.info(f"请求开始: {request.method} {path}")

        try:
            response = await call_next(request)
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            request_logger.info(
                f"请求完成: {request.method} {path} - {response.status_code} ({duration_ms:.2f}ms)"
            )
            return response

        except Exception as e:
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            request_logger.error(
                f"请求异常: {request.method} {path} - {str(e)} ({duration_ms:.2f}ms)"
            )
            raise
