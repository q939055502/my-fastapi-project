from src.core.storage import SessionLocal, cache_manager
from src.models import Tenant

def resolve_tenant_id(code):
    if code is None or code == 'platform':
        return 0 if code == 'platform' else None
    cache_key = f'code:{code}'
    cached = cache_manager.get_global(resource='tenant', key=cache_key)
    if cached is not None:
        return cached if cached != -1 else None
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter(Tenant.code == code).first()
        result = tenant.id if tenant else None
    finally:
        db.close()
    cache_value = result if result is not None else -1
    cache_manager.set_global(resource='tenant', key=cache_key, value=cache_value)
    return result
