# 顶层抽象基类
class BaseModel(DeclarativeBase):
    __abstract__ = True

    @classmethod
    def __init_subclass__(cls, **kwargs):
        """每一个业务模型子类加载时自动执行"""
        super().__init_subclass__(**kwargs)
        # 给当前模型绑定三个mapper事件，统一入口分发
        event.listen(cls, "after_insert", _cache_invalidate_dispatch)
        event.listen(cls, "after_update", _cache_invalidate_dispatch)
        event.listen(cls, "after_delete", _cache_invalidate_dispatch)



# 缓存失效依赖图：key=变更的模型名，value=需要清除的资源列表
_CACHE_DEPENDENCY_MAP = {
    "Role": ["role", "login_ctx"],           # Role变更 → 清除role和login_ctx
    "Permission": ["permission", "login_ctx"], # Permission变更 → 清除permission和login_ctx
    "RolePermission": ["role_permission", "login_ctx"],
    "RoleSubject": ["role_subject", "login_ctx"],
    "DataScopeRule": ["data_scope_rule", "login_ctx"],
    "OrgSubject": ["org_subject", "login_ctx"],
    "Member": ["member", "login_ctx"],
    "User": ["user", "login_ctx"],
    "DictType": ["dict_type"],               # DictType变更 → 只清除dict_type
    "DictData": ["dict_data"],
    "SystemConfig": ["sys_config"],
}

