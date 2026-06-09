"""
权限校验中间件

执行接口级别租户隔离和权限校验：
- 区分公开接口、登录接口、平台级接口、租户级接口
- 验证接口访问权限
"""

from fastapi import HTTPException, Request, status
from src.common.core.auth.annotations import InterfaceType
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response


class AuthMiddleware(BaseHTTPMiddleware):
    """权限校验中间件 - 执行接口级别租户隔离和权限校验"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        route = request.scope.get("route")
        if not route:
            return await call_next(request)

        # 1. 检查是否为公开接口
        if getattr(route.endpoint, "is_public", False):
            return await call_next(request)

        # 2. 获取认证上下文
        auth_ctx = getattr(request.state, "auth_context", None)

        # 3. 检查登录状态
        if not auth_ctx or not auth_ctx.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="请先登录"
            )

        # 4. 检查是否为登录即可访问接口
        if getattr(route.endpoint, "login_required", False):
            return await call_next(request)

        # 5. 获取接口类型（默认为租户级）
        itype = getattr(route.endpoint, "interface_type", InterfaceType.TENANT)

        # 6. 接口级别租户校验
        if itype == InterfaceType.PLATFORM:
            # 平台接口：必须无tenant_id，且subject_type为0
            if auth_ctx.tenant_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="无平台操作权限"
                )
            if auth_ctx.subject_type != 0:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="需要平台管理员身份"
                )
        else:
            # 租户接口：必须有tenant_id和member_id，且subject_type为1
            if auth_ctx.tenant_id is None or auth_ctx.member_id is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="请先选择租户身份"
                )
            if auth_ctx.subject_type != 1:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="需要租户成员身份"
                )

        return await call_next(request)
