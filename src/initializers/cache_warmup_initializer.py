"""
缓存预热初始化器

负责系统缓存的预热初始化

职责：
- 在系统启动时预加载常用数据到缓存
- 提高系统首次访问性能
- 减少数据库查询压力

幂等性保证：
- 缓存预热本身具有幂等性（重复执行会覆盖缓存）
- 不需要检查是否已存在

缓存键设计：
- sys_config:{code} - 系统配置缓存
- dict_type:all - 字典类型列表
- dict_data:{type_code} - 按类型分组的字典数据
- permission:{id} - 权限信息
- permission:all - 所有权限列表
- role:{id} - 角色信息
- role:{id}:permissions - 角色权限列表
- role:all - 所有角色列表
- tenant:{id} - 租户信息
- tenant:all - 所有租户列表
- user:{id} - 用户信息
- user:all - 所有用户列表
- account_bind:{user_id} - 账号绑定关系（按用户ID）
- account_bind:all - 所有账号绑定关系列表
"""

from sqlalchemy import select
from src.core.config import settings
from src.core.log import logger
from src.core.storage import get_db
from src.core.storage.cache import cache_manager


def _warmup_system_config() -> int:
    """预热系统配置缓存"""
    cache_count = 0

    for session in get_db():
        from src.models.platform import SystemConfig

        query = select(SystemConfig).where(SystemConfig.status == True)
        result = session.execute(query)
        configs = result.scalars().all()

        for config in configs:
            cache_key = f"sys_config:{config.code}"
            cache_value = {
                "id": config.id,
                "name": config.name,
                "code": config.code,
                "value": config.value,
                "config_type": config.config_type,
                "group": config.group,
                "description": config.remark,
                "typed_value": config.typed_value
            }
            cache_manager.set_global(resource="sys_config", key=config.code, value=cache_value, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
            cache_count += 1

        break

    return cache_count


def _warmup_dict_data() -> int:
    """预热字典数据缓存"""
    cache_count = 0

    for session in get_db():
        from src.models.platform import DictData, DictType

        query = select(DictType).where(DictType.status == True)
        result = session.execute(query)
        dict_types = result.scalars().all()

        type_list = []
        for dict_type in dict_types:
            type_list.append({
                "id": dict_type.id,
                "name": dict_type.name,
                "code": dict_type.code,
                "sort": dict_type.sort
            })

            data_query = select(DictData).where(
                DictData.dict_type_id == dict_type.id,
                DictData.status == True
            ).order_by(DictData.sort)
            data_result = session.execute(data_query)
            dict_datas = data_result.scalars().all()

            data_list = []
            for data in dict_datas:
                data_list.append({
                    "id": data.id,
                    "label": data.label,
                    "value": data.value,
                    "css_class": data.css_class,
                    "sort": data.sort
                })

            cache_manager.set_global(resource="dict_data", key=dict_type.code, value=data_list, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
            cache_count += 1

        cache_manager.set_global(resource="dict_type", key="all", value=type_list, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
        cache_count += 1

        break

    return cache_count


def _warmup_permission_data() -> int:
    """预热权限数据缓存"""
    cache_count = 0

    for session in get_db():
        from src.models.platform import Permission

        query = select(Permission)
        result = session.execute(query)
        permissions = result.scalars().all()

        perm_list = []
        for perm in permissions:
            perm_list.append({
                "id": perm.id,
                "name": perm.name,
                "code": perm.permission_code,
                "type": perm.type,
                "parent_id": perm.parent_id,
                "sort": perm.sort,
                "resource": perm.resource,
                "action": perm.action
            })

            cache_manager.set_global(resource="permission", key=str(perm.id), value=perm_list[-1], l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
            cache_count += 1

        cache_manager.set_global(resource="permission", key="all", value=perm_list, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
        cache_count += 1

        break

    return cache_count


def _warmup_role_data() -> int:
    """预热角色数据缓存"""
    cache_count = 0

    for session in get_db():
        from src.models.platform import Role, RolePermission

        query = select(Role)
        result = session.execute(query)
        roles = result.scalars().all()

        role_list = []
        for role in roles:
            role_cache = {
                "id": role.id,
                "name": role.name,
                "code": role.code,
                "sort": role.sort,
                "description": role.remark,
                "tenant_id": role.tenant_id
            }
            role_list.append(role_cache)

            cache_manager.set_global(resource="role", key=str(role.id), value=role_cache, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
            cache_count += 1

            permissions = []
            for role_perm in role.role_permissions:
                perm = role_perm.permission
                if perm:
                    permissions.append({
                        "id": perm.id,
                        "name": perm.name,
                        "code": perm.permission_code,
                        "type": perm.type,
                        "parent_id": perm.parent_id,
                        "sort": perm.sort
                    })

            cache_manager.set_global(resource="role", key=f"{role.id}:permissions", value=permissions, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
            cache_count += 1

        cache_manager.set_global(resource="role", key="all", value=role_list, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
        cache_count += 1

        break

    return cache_count


def _warmup_tenant_data() -> int:
    """预热租户数据缓存"""
    cache_count = 0

    for session in get_db():
        from src.models.tenant import Tenant

        query = select(Tenant).where(Tenant.status == "active")
        result = session.execute(query)
        tenants = result.scalars().all()

        tenant_list = []
        for tenant in tenants:
            tenant_cache = {
                "id": tenant.id,
                "name": tenant.name,
                "code": tenant.code,
                "status": tenant.status,
                "contact_name": tenant.contact_name,
                "contact_phone": tenant.contact_phone,
                "contact_email": tenant.contact_email,
                "company_size": tenant.company_size,
                "industry": tenant.industry,
                "owner_user_id": tenant.owner_user_id
            }
            tenant_list.append(tenant_cache)

            cache_manager.set_global(resource="tenant", key=str(tenant.id), value=tenant_cache, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
            cache_count += 1

        cache_manager.set_global(resource="tenant", key="all", value=tenant_list, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
        cache_count += 1

        break

    return cache_count


def _warmup_user_data() -> int:
    """预热用户数据缓存"""
    cache_count = 0

    for session in get_db():
        from src.models.platform import User

        query = select(User).where(User.delete_time.is_(None))
        result = session.execute(query)
        users = result.scalars().all()

        user_list = []
        for user in users:
            user_cache = {
                "id": user.id,
                "username": user.username,
                "alias": user.alias,
                "avatar": user.avatar,
                "gender": user.gender,
                "is_active": user.is_active,
                "is_multi_login": user.is_multi_login,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "last_login_ip": user.last_login_ip
            }
            user_list.append(user_cache)

            cache_manager.set_global(resource="user", key=str(user.id), value=user_cache, l1_ttl=settings.L1_CACHE_TTL_MEDIUM, l2_ttl=settings.L2_CACHE_TTL_MEDIUM)
            cache_count += 1

        cache_manager.set_global(resource="user", key="all", value=user_list, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
        cache_count += 1

        break

    return cache_count


def _warmup_account_bind_data() -> int:
    """预热账号绑定关系缓存"""
    cache_count = 0

    for session in get_db():
        from src.models.platform import AccountBind

        query = select(AccountBind).where(AccountBind.delete_time.is_(None))
        result = session.execute(query)
        binds = result.scalars().all()

        # 按用户ID分组
        account_bind_dict = {}
        all_bind_list = []

        for bind in binds:
            bind_cache = {
                "id": bind.id,
                "user_id": bind.user_id,
                "bind_type": bind.bind_type,
                "identifier": bind.identifier,
                "is_default": bind.is_default,
                "status": bind.status,
                "verified_at": bind.verified_at.isoformat() if bind.verified_at else None,
                "source": bind.source,
                "created_at": bind.created_at.isoformat() if bind.created_at else None
            }
            all_bind_list.append(bind_cache)

            # 按用户ID分组
            if bind.user_id not in account_bind_dict:
                account_bind_dict[bind.user_id] = []
            account_bind_dict[bind.user_id].append(bind_cache)

        # 缓存每个用户的绑定关系
        for user_id, bind_list in account_bind_dict.items():
            cache_manager.set_global(resource="account_bind", key=str(user_id), value=bind_list, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
            cache_count += 1

        # 缓存所有绑定关系
        cache_manager.set_global(resource="account_bind", key="all", value=all_bind_list, l1_ttl=settings.L1_CACHE_TTL_LOW, l2_ttl=settings.L2_CACHE_TTL_LOW)
        cache_count += 1

        break

    return cache_count


def init_cache_warmup():
    """
    初始化缓存预热

    预加载常用数据到缓存：
    1. 系统配置 - 全量加载
    2. 字典数据 - 按类型加载
    3. 权限数据 - 全量加载
    4. 角色数据 - 全量加载
    5. 租户数据 - 全量加载
    6. 用户数据 - 全量加载
    7. 账号绑定关系 - 全量加载

    注意：缓存预热应在数据初始化完成后执行
    确保数据已存在后再加载到缓存
    """
    logger.info("开始执行缓存预热...")

    try:
        total_count = 0

        logger.info("预热系统配置...")
        config_count = _warmup_system_config()
        logger.info(f"系统配置预热完成，共 {config_count} 条")
        total_count += config_count

        logger.info("预热字典数据...")
        dict_count = _warmup_dict_data()
        logger.info(f"字典数据预热完成，共 {dict_count} 条")
        total_count += dict_count

        logger.info("预热权限数据...")
        perm_count = _warmup_permission_data()
        logger.info(f"权限数据预热完成，共 {perm_count} 条")
        total_count += perm_count

        logger.info("预热角色数据...")
        role_count = _warmup_role_data()
        logger.info(f"角色数据预热完成，共 {role_count} 条")
        total_count += role_count

        logger.info("预热租户数据...")
        tenant_count = _warmup_tenant_data()
        logger.info(f"租户数据预热完成，共 {tenant_count} 条")
        total_count += tenant_count

        logger.info("预热用户数据...")
        user_count = _warmup_user_data()
        logger.info(f"用户数据预热完成，共 {user_count} 条")
        total_count += user_count

        logger.info("预热账号绑定关系...")
        account_bind_count = _warmup_account_bind_data()
        logger.info(f"账号绑定关系预热完成，共 {account_bind_count} 条")
        total_count += account_bind_count

        logger.info(f"缓存预热完成，共加载 {total_count} 条缓存记录")

    except Exception as e:
        logger.error(f"缓存预热失败: {str(e)}")
        raise
