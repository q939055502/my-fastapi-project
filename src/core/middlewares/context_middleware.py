"""
请求上下文中间件

统一管理请求上下文，并自动记录请求日志：
- 请求进入时记录请求开始
- 请求结束时记录请求完成
- 异常时记录错误日志
"""

import uuid
from datetime import datetime

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.core.auth import parse_jwt_token
from src.core.context import AuthContext, create_log_context, set_log_context
from src.core.log import logger


class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件 - 处理上下文设置和日志记录"""

    async def _get_user_info(self, request: Request) -> tuple:
        """从请求的 JWT 中获取用户信息"""
        tenant_id = None
        user_id = None
        member_id = None
        username = ""
        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header[len("Bearer "):]
                payload = parse_jwt_token(token)
                if payload:
                    user_id = payload.get("user_id")
                    username = payload.get("username", "")
                    tenant_id = payload.get("tenant_id")
                    member_id = payload.get("member_id")
        except Exception:
            pass
        return tenant_id, user_id, member_id, username

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """处理请求并设置上下文"""
        start_time = datetime.now()

        # 生成请求ID（优先从请求头获取，不存在则生成新的）
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # 获取用户信息
        tenant_id, user_id, member_id, username = await self._get_user_info(request)

        # 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"

        # 创建认证上下文对象
        auth_context = AuthContext(
            request_id=request_id,
            user_id=user_id,
            username=username,
            tenant_id=tenant_id,
            member_id=member_id,
            client_ip=client_ip,
        )

        # 存储到请求状态中
        request.state.auth_context = auth_context

        # 创建并设置日志上下文（用于整个请求链路）
        log_ctx = create_log_context(
            request_id=request_id,
            tenant_id=tenant_id,
            user_id=user_id,
            ip=client_ip,
            endpoint=request.url.path,
        )
        set_log_context(log_ctx)

        # 构建日志上下文
        extra = {
            "request_id": request_id,
            "tenant_id": str(tenant_id) if tenant_id else "system",
            "user_id": str(user_id) if user_id else "0",
            "ip": client_ip,
            "endpoint": request.url.path,
            "duration": "0ms",
            "business_code": "-",
        }

        # 记录请求开始
        request_logger = logger.bind(**extra)
        request_logger.info(f"请求开始: {request.method} {request.url.path}")

        try:
            # 处理请求
            response = await call_next(request)

            # 计算耗时
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            duration_str = f"{duration_ms:.0f}ms"

            # 更新日志上下文
            extra.update({
                "duration": duration_str,
                "business_code": str(response.status_code),
            })

            # 记录请求完成
            request_logger = logger.bind(**extra)
            request_logger.info(
                f"请求完成: {request.method} {request.url.path} - {response.status_code} ({duration_ms:.2f}ms)"
            )

            # 在响应头中添加请求ID
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # 计算耗时
            end_time = datetime.now()
            duration_ms = (end_time - start_time).total_seconds() * 1000
            duration_str = f"{duration_ms:.0f}ms"

            # 更新日志上下文（异常情况）
            extra.update({
                "duration": duration_str,
                "business_code": "ERROR",
            })

            # 记录请求异常（ERROR级别）
            request_logger = logger.bind(**extra)
            request_logger.error(
                f"请求异常: {request.method} {request.url.path} - {str(e)} ({duration_ms:.2f}ms)"
            )

            raise
