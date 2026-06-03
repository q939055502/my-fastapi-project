from contextvars import ContextVar

# 定义 ContextVar
auth_context_var: ContextVar[AuthContext] = ContextVar("auth_context")

def get_auth_context_var() -> AuthContext:
    """获取当前上下文"""
    return auth_context_var.get(AuthContext())

def set_auth_context_var(context: AuthContext) -> None:
    """设置当前上下文"""
    auth_context_var.set(context)




    from src.core.auth.context import set_auth_context_var, AuthContext

async def dispatch(self, request: Request, call_next):
    # ... 创建 context
    set_auth_context_var(auth_context)  # 设置到 ContextVar
    request.state.auth_context = auth_context  # 同时保留 request.state


def get_logger() -> loguru_logger:
    """获取带当前上下文的 logger"""
    from src.core.auth.context import get_auth_context_var
    ctx = get_auth_context_var()
    return logger.bind(
        request_id=ctx.request_id,
        tenant_id=str(ctx.tenant_id) if ctx.tenant_id else "system",
        user_id=str(ctx.user_id) if ctx.user_id else "0",
        ip=ctx.client_ip,
        endpoint=ctx.endpoint if hasattr(ctx, "endpoint") else "-",
        duration="0ms",
        business_code="-",
    )