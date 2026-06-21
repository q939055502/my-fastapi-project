# main.py
app = FastAPI()

@app.middleware("http")
async def validation_middleware(request, call_next):
    ctx = request.state.auth_context
    if ctx and ctx.interface_type == InterfaceType.TENANT and ctx.tenant_id is None:
        return JSONResponse(status_code=401, content={"detail": "未选择租户"})
    if ctx and ctx.tenant_id and ctx.path_tenant_id and ctx.tenant_id != ctx.path_tenant_id:
        return JSONResponse(status_code=403, content={"detail": "越权访问"})
    
    response = await call_next(request)
    return response







    