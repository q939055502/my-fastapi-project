# 1. 新增查询上下文（用于特殊场景标记）
# src/core/contexts/query_context.py
from contextvars import ContextVar

_query_context = ContextVar("query_context", default={})

def set_query_context(**kwargs):
    """设置查询上下文标记"""
    _query_context.set(kwargs)

def get_query_context():
    """获取查询上下文标记"""
    return _query_context.get()

# 2. before_compile 中检查标记
@event.listens_for(Query, "before_compile", retval=True)
def apply_data_permissions(query):
    query_ctx = get_query_context()
    
    # 标记跳过 → 直接返回
    if query_ctx.get("skip_data_permission"):
        return query
    
    # 标记跳过租户 → 只保留数据范围
    if query_ctx.get("skip_tenant"):
        # ... 只过滤数据范围，不过滤租户
        return query
    
    # 正常逻辑...