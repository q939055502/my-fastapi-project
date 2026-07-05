"""ORM 事件缓存联动

监听 SQLAlchemy Session 事件，写操作后自动清除相关缓存。
按 ORM 模型名 → 缓存资源名 映射，清对应 resource 的所有缓存。

注意：
- 本模块属于缓存层，放在 src/core/storage/cache/ 下
- 只依赖 SQLAlchemy 和 cache_manager，不依赖业务逻辑
- 如需新增模型映射，在 _CACHE_RESOURCE_MAP 中添加即可
"""

from sqlalchemy import event
from sqlalchemy.orm import Session

from .cache_manager import cache_manager


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
    "SystemConfig": "sys_config",
    "Tenant": "tenant",
    "AccountBind": "account_bind",
}


_LOGIN_CTX_IMPACT_MODELS = {
    "Role", "Permission",
    "RoleSubject", "RolePermission", "DataScopeRule",
    "OrgSubject", "Member", "User",
}


def _clear_all(resource: str) -> None:
    cache_manager.increment_version(namespace=resource)


@event.listens_for(Session, 'after_flush')
def after_flush_cache(session, flush_context):
    """写操作后自动清除缓存（通用失效）

    通过递增版本号使对应 resource 下所有缓存失效。
    """
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
        cache_manager.increment_version(namespace="login_ctx")


def register_cache_events() -> None:
    """注册缓存事件监听

    显式调用一次确保事件被注册（导入模块时也会自动注册）。
    """
    pass