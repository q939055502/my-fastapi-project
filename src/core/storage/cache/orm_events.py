"""ORM 事件缓存联动（Tag 机制）

监听 SQLAlchemy Session after_flush 事件，写操作后自动递增相关标签版本。

标签策略:
1. 表级标签: 任何对该模型的写操作都递增 "{entity}:all"
2. 行级标签: 如果能获取实例主键，递增 "{entity}:{id}"
3. 联动标签: 权限相关模型变更时，联动递增 "login_ctx:all"

注意:
- 只注册一次 after_flush，不再有重复监听
- 批量 DELETE/UPDATE 语句不触发 after_flush，业务层需手动调用 invalidate
- 如需新增模型映射，在 _CACHE_TABLE_TAG_MAP 中添加即可
"""

from sqlalchemy import event
from sqlalchemy.orm import Session

from .tag_store import tag_store


# 模型名 → 表级标签（任何写操作都递增）
_CACHE_TABLE_TAG_MAP = {
    "Role": "role:all",
    "Permission": "perm:all",
    "RolePermission": "role_perm:all",
    "RoleSubject": "role_subject:all",
    "DataScopeRule": "data_scope:all",
    "User": "user:all",
    "Member": "member:all",
    "Org": "org:all",
    "OrgSubject": "org_subject:all",
    "DictType": "dict_type:all",
    "DictData": "dict_data:all",
    "SystemConfig": "sys_config:all",
    "Tenant": "tenant:all",
    "AccountBind": "account_bind:all",
}

# 模型名 → 主键字段名（用于生成行级标签）
_CACHE_ROW_TAG_MAP = {
    "Role": "id",
    "Permission": "id",
    "User": "id",
    "Tenant": "id",
    "Member": "id",
    "Org": "id",
    "DictType": "id",
    "DictData": "id",
    "SystemConfig": "id",
    "AccountBind": "id",
}

# 权限相关模型，变更时联动递增 login_ctx 标签
_LOGIN_CTX_IMPACT_MODELS = {
    "Role", "Permission",
    "RoleSubject", "RolePermission", "DataScopeRule",
    "OrgSubject", "Member", "User",
}


@event.listens_for(Session, 'after_flush')
def after_flush_cache(session, flush_context):
    """写操作后自动递增相关标签版本

    遍历 session.new / dirty / deleted 中的实例，按模型类型递增:
    - 表级标签: {entity}:all
    - 行级标签: {entity}:{id}（如果主键可用）
    - 联动标签: login_ctx:all（权限相关模型变更时）
    """
    tags_to_increment = set()
    need_login_ctx_clear = False

    for instance in list(session.new) + list(session.dirty) + list(session.deleted):
        model_name = type(instance).__name__

        # 表级标签
        table_tag = _CACHE_TABLE_TAG_MAP.get(model_name)
        if table_tag:
            tags_to_increment.add(table_tag)

        # 行级标签
        pk_field = _CACHE_ROW_TAG_MAP.get(model_name)
        if pk_field:
            pk_value = getattr(instance, pk_field, None)
            if pk_value is not None:
                entity_name = model_name.lower()
                tags_to_increment.add(f"{entity_name}:{pk_value}")

        # 联动 login_ctx
        if model_name in _LOGIN_CTX_IMPACT_MODELS:
            need_login_ctx_clear = True

    if need_login_ctx_clear:
        tags_to_increment.add("login_ctx:all")

    if tags_to_increment:
        tag_store.invalidate(list(tags_to_increment))


def register_cache_events() -> None:
    """注册缓存事件监听

    导入模块时 @event.listens_for 装饰器自动注册。
    此函数保留兼容性，显式调用也安全（pass）。
    """
    pass
