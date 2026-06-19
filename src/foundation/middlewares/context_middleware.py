"""请求上下文中间件

统一管理请求上下文:
- 设置认证上下文(AuthContext)
- 设置日志上下文(LogContext)
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.core.log import create_log_context, set_log_context
from src.foundation.iam.auth.context import AuthContext, set_auth_context
from src.foundation.iam.auth.security import parse_jwt_token
from src.foundation.tenant.resolver import resolve_tenant_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    """请求上下文中间件 - 处理上下文设置"""

    PUBLIC_PATH_PREFIXES = ("/v1/platform", "/docs", "/openapi.json", "/redoc")

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """处理请求并设置上下文"""

        # 1. 生成请求ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # 2. 解析路径租户信息
        path_tenant_id = self._resolve_path_tenant(request)

        # 3. 解析认证信息(从JWT)
        auth_info = await self._parse_auth_info(request)
        auth_tenant_id = auth_info.get("tenant_id")
        user_id = auth_info.get("user_id")
        member_id = auth_info.get("member_id")
        username = auth_info.get("username")

        # 4. 确定主体类型和主体ID
        subject_type = 1 if auth_tenant_id and auth_tenant_id > 0 else 0
        subject_id = member_id if auth_tenant_id and auth_tenant_id > 0 else user_id

        # 5. 获取客户端IP
        client_ip = request.client.host if request.client else "unknown"

        # 6. 创建认证上下文对象
        auth_context = AuthContext(
            request_id=request_id,
            user_id=user_id,
            username=username,
            tenant_id=auth_tenant_id,
            path_tenant_id=path_tenant_id,
            member_id=member_id,
            client_ip=client_ip,
            subject_type=subject_type,
            subject_id=subject_id,
        )

        # 7. 存储到请求状态中(供路由层使用)
        request.state.auth_context = auth_context

        # 8. 存储到 ContextVar(供非路由层使用)
        set_auth_context(auth_context)

        # 9. 设置日志上下文
        log_ctx = create_log_context(
            request_id=request_id,
            tenant_id=auth_tenant_id,
            user_id=user_id,
            ip=client_ip,
            endpoint=request.url.path,
        )
        set_log_context(log_ctx)

        # 10. 设置响应头
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    def _resolve_path_tenant(self, request: Request) -> int | None:
        """从请求路径解析 tenant_id"""
        if request.url.path.startswith(self.PUBLIC_PATH_PREFIXES):
            return None

        tenant_key = request.path_params.get("tenant_key")
        if not tenant_key:
            return None

        tenant_id = resolve_tenant_id(tenant_key)

        if tenant_id is not None:
            request.path_params["tenant_key"] = str(tenant_id)

        return tenant_id

    async def _parse_auth_info(self, request: Request) -> dict:
        """从请求的 JWT 中解析认证信息"""
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

        return {
            "tenant_id": tenant_id,
            "user_id": user_id,
            "member_id": member_id,
            "username": username,
        }
