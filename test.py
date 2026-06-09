# 资源类型枚举
class ResourceType:
    PLATFORM = "platform"  # 平台级资源
    TENANT = "tenant"      # 租户级资源
    BOTH = "both"          # 两者都适用

# 修改资源注册
def register_resource(resource_name: str, model_class, resource_type: str = ResourceType.TENANT):
    RESOURCE_MODEL_MAP[resource_name] = {
        "model": model_class,
        "type": resource_type
    }






@event.listens_for(Query, "before_compile", retval=True)
def apply_data_permissions(query):
    try:
        entities = []
        for desc in query.column_descriptions:
            if hasattr(desc['type'], '__table__'):
                entities.append(desc['type'])
        
        if not entities:
            return query
        
        ctx = get_auth_context()
        
        if not ctx.user_id:
            return query
        
        if is_super_admin(ctx.user_id):
            return query
        
        # 区分平台级和租户级资源
        for entity in entities:
            resource_info = None
            for res, info in RESOURCE_MODEL_MAP.items():
                if info['model'] == entity:
                    resource_info = info
                    break
            
            if not resource_info:
                continue
            
            # 平台级资源：不过滤租户
            if resource_info['type'] == ResourceType.PLATFORM:
                continue
            
            # 租户级资源：应用租户隔离
            if ctx.tenant_id and ctx.tenant_id > 0:
                if hasattr(entity, 'tenant_id'):
                    query = query.filter(entity.tenant_id == ctx.tenant_id)
        
        # 应用数据权限范围（scope）
        # ... 现有逻辑 ...
        
        return query
    
    except Exception:
        return query









# 装饰器：标记接口为平台级
def platform_api(func):
    """标记接口为平台级，不受租户隔离限制"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # 在请求上下文中标记为平台级操作
        request = args[0] if args else None
        if request and hasattr(request, 'state'):
            request.state.is_platform_api = True
        return await func(*args, **kwargs)
    return wrapper