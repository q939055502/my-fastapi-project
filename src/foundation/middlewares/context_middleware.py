import uuid as uuid_module
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from src.core.log import create_log_context, set_log_context
from src.core.storage import SessionLocal
from src.core.storage.uuid_resolver import uuid_resolver
from src.foundation.iam.auth.context import AuthContext, set_auth_context
from src.foundation.iam.auth.security import parse_jwt_token
from src.foundation.tenant.resolver import resolve_tenant_id

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
        auth_context = AuthContext(
            request_id=request_id,
            user_id=auth_info.get('user_id'),
            username=auth_info.get('username'),
            tenant_id=auth_info.get('tenant_id'),
            path_tenant_id=path_tenant_id,
            member_id=auth_info.get('member_id'),
            client_ip=client_ip,
        )
        request.state.auth_context = auth_context
        set_auth_context(auth_context)
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
        except Exception:
            pass
        return {'tenant_id': tenant_id, 'user_id': user_id, 'member_id': member_id, 'username': username}
