"""SQLAlchemy Session after_flush 缓存联动失效

写操作后自动清缓存，一次注册零遗漏。
按 ORM 模型名 → 缓存资源名 映射，清对应 resource 的所有缓存。
同时联动清 login_ctx（权限类模型变更时）。
"""

from sqlalchemy import event
from sqlalchemy.orm import Session

from src.core.storage import cache_manager


_CACHE_RESOURCE_MAP = {
    "Role": "role",
    "Permission": "permission",
    "RolePermission": "role_permission",
    "RoleSubject": "role_subject",
    "DataScopeRule": "data_scope_rule",
    "User": "user",
    "Member": "member",
    "Org": "org",
    "OrgSubject": "org_subject",
    "DictType": "dict_type",
    "DictData": "dict_data",
}


_LOGIN_CTX_IMPACT_MODELS = {
    "Role", "Permission",
    "RoleSubject", "RolePermission", "DataScopeRule",
    "OrgSubject", "Member", "User",
}


def _clear_all(resource: str):
    cache_manager._clear_pattern_raw(f"global:{resource}:*")


@event.listens_for(Session, 'after_flush')
def after_flush_cache(session, flush_context):
    """写操作后自动清缓存（通用失效）"""
    affected_resources = set()
    need_login_ctx_clear = False

    for instance in list(session.new) + list(session.dirty) + list(session.deleted):
        model_name = type(instance).__name__
        resource = _CACHE_RESOURCE_MAP.get(model_name)

        if resource:
            affected_resources.add(resource)
        if model_name in _LOGIN_CTX_IMPACT_MODELS:
            need_login_ctx_clear = True

    for resource in affected_resources:
        _clear_all(resource)

    if need_login_ctx_clear:
        cache_manager._clear_pattern_raw("global:login_ctx:*")
