import logging
import uuid as uuid_module

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.routing import Match

from src.core.annotations import InterfaceType
from src.core.exceptions import BusinessException
from src.core.log import create_log_context, set_log_context
from src.core.storage import SessionLocal
from src.core.storage.uuid_resolver import uuid_resolver
from src.foundation.iam.auth.context import AuthContext, set_auth_context
from src.foundation.iam.auth.security import parse_jwt_token
from src.foundation.tenant.resolver import resolve_tenant_id

logger = logging.getLogger(__name__)


def _is_valid_uuid(s):
    try:
        uuid_module.UUID(s)
        return True
    except (ValueError, AttributeError, TypeError):
        return False


class RequestContextMiddleware(BaseHTTPMiddleware):
    PUBLIC_PATH_PREFIXES = ('/v1/platform', '/docs', '/openapi.json', '/redoc')

    async def dispatch(self, request, call_next):
        request_id = request.headers.get('X-Request-ID') or str(uuid_module.uuid4())
        path_tenant_id = self._resolve_path_tenant(request)
        auth_info = await self._parse_auth_info(request)
        client_ip = request.client.host if request.client else 'unknown'
        interface_type = self._resolve_interface_type(request)

        auth_context = AuthContext(
            request_id=request_id,
            user_id=auth_info.get('user_id'),
            username=auth_info.get('username'),
            tenant_id=auth_info.get('tenant_id'),
            path_tenant_id=path_tenant_id,
            member_id=auth_info.get('member_id'),
            client_ip=client_ip,
            interface_type=interface_type,
        )

        request.state.auth_context = auth_context
        set_auth_context(auth_context)

        self._validate_tenant_scope(auth_context)

        log_ctx = create_log_context(
            request_id=request_id,
            tenant_id=auth_info.get('tenant_id'),
            user_id=auth_info.get('user_id'),
            ip=client_ip,
            endpoint=request.url.path,
        )
        set_log_context(log_ctx)

        response = await call_next(request)
        response.headers['X-Request-ID'] = request_id
        return response

    def _validate_tenant_scope(self, ctx):
        """校验租户上下文一致性

        - TENANT 接口类型必须已选租户，且与 path_tenant_id 一致
        - ALL 接口需要校验两者一致性
        - PUBLIC / PLATFORM 不做校验
        """
        interface_type = ctx.interface_type

        if interface_type is None or interface_type == InterfaceType.PUBLIC:
            return None

        elif interface_type == InterfaceType.PLATFORM:
            # 平台接口不做租户校验，允许已选租户的用户访问
            return None

        elif interface_type == InterfaceType.TENANT:
            if ctx.tenant_id is None or ctx.member_id is None or ctx.tenant_id < 1 or ctx.member_id < 1:
                logger.warning("租户接口但未选择租户, path_tenant_id=%s, member_id=%s", ctx.path_tenant_id, ctx.member_id)
                raise BusinessException(40100, "未选择租户")
            if ctx.path_tenant_id is None or ctx.tenant_id != ctx.path_tenant_id:
                logger.warning(
                    "租户越权: tenant_id=%s, path_tenant_id=%s, member_id=%s, username=%s",
                    ctx.tenant_id, ctx.path_tenant_id, ctx.member_id, ctx.username,
                )
                raise BusinessException(40300, "无权访问该租户数据")

        elif interface_type == InterfaceType.ALL:
            if ctx.path_tenant_id is not None and ctx.path_tenant_id > 0:
                if ctx.tenant_id is None or ctx.member_id is None or ctx.tenant_id < 1 or ctx.member_id < 1 or ctx.tenant_id != ctx.path_tenant_id:
                    logger.warning(
                        "租户越权: tenant_id=%s, path_tenant_id=%s, member_id=%s, username=%s",
                        ctx.tenant_id, ctx.path_tenant_id, ctx.member_id, ctx.username,
                    )
                    raise BusinessException(40300, "无权访问该租户数据")
        

    def _resolve_interface_type(self, request):
        app = request.scope.get('app') or request.scope.get('starlette.app')
        if app is None:
            return None
        for route in app.routes:
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                handler = getattr(route, 'endpoint', None)
                if handler is None:
                    continue
                itype = getattr(handler, 'interface_type', None)
                if itype is not None:
                    return itype
                return None
        return None

    def _resolve_path_tenant(self, request):
        if request.url.path.startswith(self.PUBLIC_PATH_PREFIXES):
            return None
        identifier = request.path_params.get('tenant_key') or request.path_params.get('tenant_uuid')
        if not identifier:
            return None
        if identifier == 'platform':
            return 0
        if _is_valid_uuid(identifier):
            db = SessionLocal()
            try:
                return uuid_resolver.resolve(db, 'platform_tenant', identifier)
            except Exception as e:
                logger.debug("tenant UUID 解析失败: %s", e)
                return None
            finally:
                db.close()
        return resolve_tenant_id(identifier)

    async def _parse_auth_info(self, request):
        tenant_id = None; user_id = None; member_id = None; username = ''
        try:
            h = request.headers.get('Authorization', '')
            if h.startswith('Bearer '):
                payload = parse_jwt_token(h[7:])
                if payload:
                    user_id = payload.get('user_id')
                    username = payload.get('username', '')
                    tenant_id = payload.get('tenant_id')
                    member_id = payload.get('member_id')
        except Exception as e:
            logger.debug("JWT 解析失败: %s", e)
        return {'tenant_id': tenant_id, 'user_id': user_id, 'member_id': member_id, 'username': username}