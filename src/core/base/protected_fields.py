"""字段保护常量

Repository 基类创建 / 更新时自动过滤的安全敏感字段，
防止前端传入覆盖系统级字段。

用法:
  from src.core.base.protected_fields import CREATE_PROTECTED_FIELDS, UPDATE_PROTECTED_FIELDS
"""


CREATE_PROTECTED_FIELDS = {
    "id",
    "tenant_id",
    "delete_time",
    "is_system",
}


UPDATE_PROTECTED_FIELDS = {
    "id",
    "tenant_id",
    "delete_time",
    "is_system",
    "creator_id",
    "creator_type",
    "updater_id",
    "updater_type",
    "created_at",
    "updated_at",
}
