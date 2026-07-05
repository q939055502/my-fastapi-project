"""
缓存预热初始化器

负责系统缓存的预热初始化：
- 在系统启动时预加载常用数据到缓存
- 提高系统首次访问性能
- 减少数据库查询压力

幂等性保证:缓存预热本身具有幂等性(重复执行会覆盖缓存)

缓存键设计:
- sys_config:{code} - 系统配置缓存
- dict_type:all - 字典类型列表
- dict_data:{type_code} - 按类型分组的字典数据
- permission:{id} - 权限信息
- permission:all - 所有权限列表
- role:{id} - 角色信息
- role:{id}:permissions - 角色权限列表
- role:all - 所有角色列表
- role_subject:{subject_type}:{subject_id} - 主体的角色列表
- role_subject:all - 所有角色主体关联
- data_scope_rule:{role_id}:{permission_id} - 角色+权限对应的数据范围规则
- data_scope_rule:all - 所有数据范围规则
- org:{id} - 组织节点信息
- org:all - 所有组织节点
- org_closure:{org_id} - 组织闭包表(该节点所有后代)
- org_subject:{subject_type}:{subject_id} - 主体归属的组织节点
- org_subject:all - 所有组织主体关联
- tenant:{id} - 租户信息
- tenant:all - 所有租户列表
- user:{id} - 用户信息
- user:all - 所有用户列表
- member:{id} - 租户成员信息
- member:tenant:{tenant_id} - 租户下所有成员
- account_bind:{user_id} - 账号绑定关系(按用户ID)
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

        query = select(SystemConfig).where(SystemConfig.status.is_(True))
        result = session.execute(query)
        configs = result.scalars().all()

        for config in configs:
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
            cache_manager.set_global(
                resource="sys_config",
                key=config.code,
                value=cache_value,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1
        break
    return cache_count


def _warmup_dict_data() -> int:
    """预热字典数据缓存"""
    cache_count = 0
    for session in get_db():
        from src.models.platform import DictData, DictType

        query = select(DictType).where(DictType.status.is_(True))
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
                DictData.status.is_(True)
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

            cache_manager.set_global(
                resource="dict_data",
                key=dict_type.code,
                value=data_list,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1

        cache_manager.set_global(
            resource="dict_type",
            key="all",
            value=type_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
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

            cache_manager.set_global(
                resource="permission",
                key=str(perm.id),
                value=perm_list[-1],
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1

        cache_manager.set_global(
            resource="permission",
            key="all",
            value=perm_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1
        break
    return cache_count


def _warmup_role_data() -> int:
    """预热角色数据缓存"""
    cache_count = 0
    for session in get_db():
        from src.models.platform import Role

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

            cache_manager.set_global(
                resource="role",
                key=str(role.id),
                value=role_cache,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
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

            cache_manager.set_global(
                resource="role",
                key=f"{role.id}:permissions",
                value=permissions,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1

        cache_manager.set_global(
            resource="role",
            key="all",
            value=role_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1
        break
    return cache_count


def _warmup_role_subject_data() -> int:
    """预热角色-主体关联缓存

    按主体维度分组,方便权限校验时直接取角色列表。
    """
    cache_count = 0
    for session in get_db():
        from src.models.platform import RoleSubject

        query = select(RoleSubject)
        result = session.execute(query)
        role_subjects = result.scalars().all()

        all_list = []
        subject_map: dict[str, list[int]] = {}

        for rs in role_subjects:
            item = {
                "id": rs.id,
                "subject_id": rs.subject_id,
                "subject_type": rs.subject_type,
                "role_id": rs.role_id,
                "tenant_id": rs.tenant_id,
                "creator_id": rs.creator_id,
                "creator_type": rs.creator_type,
                "updater_id": rs.updater_id,
                "updater_type": rs.updater_type,
                "created_at": rs.created_at.isoformat() if rs.created_at else None,
                "updated_at": rs.updated_at.isoformat() if rs.updated_at else None,
            }
            all_list.append(item)

            key = f"{rs.subject_type}:{rs.subject_id}"
            if key not in subject_map:
                subject_map[key] = []
            subject_map[key].append(rs.role_id)

            cache_count += 1

        cache_manager.set_global(
            resource="role_subject",
            key="all",
            value=all_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1

        for key, role_ids in subject_map.items():
            cache_manager.set_global(
                resource="role_subject",
                key=key,
                value=role_ids,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1

        break
    return cache_count


def _warmup_data_scope_rule_data() -> int:
    """预热数据范围规则缓存

    按 role_id+permission_id 维度分组,方便数据范围过滤时直接取规则列表。
    """
    cache_count = 0
    for session in get_db():
        from src.models.platform import DataScopeRule

        query = select(DataScopeRule)
        result = session.execute(query)
        rules = result.scalars().all()

        all_list = []
        perm_map: dict[str, list[dict]] = {}

        for rule in rules:
            item = {
                "id": rule.id,
                "role_id": rule.role_id,
                "permission_id": rule.permission_id,
                "dimension_type": rule.dimension_type,
                "match_type": rule.match_type,
                "dimension_value": rule.dimension_value,
                "sort": rule.sort,
                "remark": rule.remark,
                "tenant_id": rule.tenant_id,
                "created_at": rule.created_at.isoformat() if rule.created_at else None,
                "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
            }
            all_list.append(item)

            key = f"{rule.role_id}:{rule.permission_id}"
            if key not in perm_map:
                perm_map[key] = []
            perm_map[key].append({
                "dimension_type": rule.dimension_type,
                "match_type": rule.match_type,
                "dimension_value": rule.dimension_value,
            })

            cache_count += 1

        cache_manager.set_global(
            resource="data_scope_rule",
            key="all",
            value=all_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1

        for key, rule_list in perm_map.items():
            cache_manager.set_global(
                resource="data_scope_rule",
                key=key,
                value=rule_list,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1

        break
    return cache_count


def _warmup_org_data() -> int:
    """预热组织节点缓存"""
    cache_count = 0
    for session in get_db():
        from src.models.platform import Org

        query = select(Org)
        result = session.execute(query)
        orgs = result.scalars().all()

        org_list = []
        for org in orgs:
            org_cache = {
                "id": org.id,
                "name": org.name,
                "code": org.code,
                "parent_id": org.parent_id,
                "level": org.level,
                "leader": org.leader,
                "phone": org.phone,
                "email": org.email,
                "status": org.status,
                "sort": org.sort,
                "remark": org.remark,
                "tenant_id": org.tenant_id,
            }
            org_list.append(org_cache)

            cache_manager.set_global(
                resource="org",
                key=str(org.id),
                value=org_cache,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1

        cache_manager.set_global(
            resource="org",
            key="all",
            value=org_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1
        break
    return cache_count


def _warmup_org_closure_data() -> int:
    """预热组织闭包表缓存

    按祖先节点维度分组,查某个节点所有后代时直接取列表。
    """
    cache_count = 0
    for session in get_db():
        from src.models.platform import OrgClosure

        query = select(OrgClosure)
        result = session.execute(query)
        closures = result.scalars().all()

        closure_map: dict[str, list[dict]] = {}

        for cl in closures:
            key = str(cl.ancestor)
            if key not in closure_map:
                closure_map[key] = []
            closure_map[key].append({
                "descendant": cl.descendant,
                "level": cl.level,
            })

            cache_count += 1

        for key, descendants in closure_map.items():
            cache_manager.set_global(
                resource="org_closure",
                key=key,
                value=descendants,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1

        cache_manager.set_global(
            resource="org_closure",
            key="all",
            value=[
                {"ancestor": cl.ancestor, "descendant": cl.descendant, "level": cl.level}
                for cl in closures
            ],
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1
        break
    return cache_count


def _warmup_org_subject_data() -> int:
    """预热成员-组织关联缓存

    按成员维度分组,查某个成员归属的 org_id 列表。
    """
    cache_count = 0
    for session in get_db():
        from src.models.platform import OrgSubject

        query = select(OrgSubject)
        result = session.execute(query)
        org_subjects = result.scalars().all()

        all_list = []
        subject_map: dict[str, list[int]] = {}

        for os_obj in org_subjects:
            item = {
                "id": os_obj.id,
                "member_id": os_obj.member_id,
                "org_id": os_obj.org_id,
                "created_at": os_obj.created_at.isoformat() if os_obj.created_at else None,
                "updated_at": os_obj.updated_at.isoformat() if os_obj.updated_at else None,
            }
            all_list.append(item)

            key = str(os_obj.member_id)
            if key not in subject_map:
                subject_map[key] = []
            subject_map[key].append(os_obj.org_id)

            cache_count += 1

        cache_manager.set_global(
            resource="org_subject",
            key="all",
            value=all_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1

        for key, org_ids in subject_map.items():
            cache_manager.set_global(
                resource="org_subject",
                key=key,
                value=org_ids,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
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

            cache_manager.set_global(
                resource="tenant",
                key=str(tenant.id),
                value=tenant_cache,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1

        cache_manager.set_global(
            resource="tenant",
            key="all",
            value=tenant_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
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

            cache_manager.set_global(
                resource="user",
                key=str(user.id),
                value=user_cache,
                l1_ttl=settings.L1_CACHE_TTL_MEDIUM,
                l2_ttl=settings.L2_CACHE_TTL_MEDIUM
            )
            cache_count += 1

        cache_manager.set_global(
            resource="user",
            key="all",
            value=user_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1
        break
    return cache_count


def _warmup_member_data() -> int:
    """预热租户成员缓存

    按成员ID和租户ID两个维度缓存:
    - member:{id}          单个成员基本信息
    - member:tenant:{tid}  某个租户下所有成员
    """
    cache_count = 0
    for session in get_db():
        from src.models.tenant import Member

        query = select(Member).where(Member.delete_time.is_(None))
        result = session.execute(query)
        members = result.scalars().all()

        member_list = []
        tenant_map: dict[str, list[dict]] = {}

        for member in members:
            member_cache = {
                "id": member.id,
                "user_id": member.user_id,
                "tenant_id": member.tenant_id,
                "subject_id": member.subject_id,
                "is_owner": member.is_owner,
                "contact_info": member.contact_info,
                "join_type": member.join_type,
                "audit_status": member.audit_status,
                "is_muted": member.is_muted,
                "joined_at": member.joined_at.isoformat() if member.joined_at else None,
                "last_login_at": member.last_login_at.isoformat() if member.last_login_at else None,
            }
            member_list.append(member_cache)

            cache_manager.set_global(
                resource="member",
                key=str(member.id),
                value=member_cache,
                l1_ttl=settings.L1_CACHE_TTL_MEDIUM,
                l2_ttl=settings.L2_CACHE_TTL_MEDIUM
            )
            cache_count += 1

            tenant_key = str(member.tenant_id)
            if tenant_key not in tenant_map:
                tenant_map[tenant_key] = []
            tenant_map[tenant_key].append(member_cache)

        cache_manager.set_global(
            resource="member",
            key="all",
            value=member_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1

        for tid, t_members in tenant_map.items():
            cache_manager.set_global(
                resource="member",
                key=f"tenant:{tid}",
                value=t_members,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
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

            if bind.user_id not in account_bind_dict:
                account_bind_dict[bind.user_id] = []
            account_bind_dict[bind.user_id].append(bind_cache)

        for user_id, bind_list in account_bind_dict.items():
            cache_manager.set_global(
                resource="account_bind",
                key=str(user_id),
                value=bind_list,
                l1_ttl=settings.L1_CACHE_TTL_LOW,
                l2_ttl=settings.L2_CACHE_TTL_LOW
            )
            cache_count += 1

        cache_manager.set_global(
            resource="account_bind",
            key="all",
            value=all_bind_list,
            l1_ttl=settings.L1_CACHE_TTL_LOW,
            l2_ttl=settings.L2_CACHE_TTL_LOW
        )
        cache_count += 1
        break
    return cache_count


def init_cache_warmup():
    """
    初始化缓存预热

    预加载常用数据到缓存:
    1. 系统配置 - 全量加载
    2. 字典数据 - 按类型加载
    3. 权限数据 - 全量加载
    4. 角色数据 - 全量加载 + 每个角色的权限列表
    5. 角色-主体关联 - 全量加载 + 按主体维度索引
    6. 数据范围规则 - 全量加载 + 按角色+权限维度索引
    7. 组织节点 - 全量加载
    8. 组织闭包表 - 按祖先节点索引(树形查询用)
    9. 组织-主体关联 - 全量加载 + 按主体维度索引
    10. 租户数据 - 全量加载
    11. 用户数据 - 全量加载
    12. 租户成员 - 全量加载 + 按租户维度索引
    13. 账号绑定关系 - 全量加载

    注意:缓存预热应在数据初始化完成后执行,确保数据已存在后再加载到缓存。
    """
    logger.info("开始执行缓存预热...")

    try:
        total_count = 0

        logger.info("预热系统配置...")
        count = _warmup_system_config()
        logger.info(f"系统配置预热完成,共 {count} 条记录")
        total_count += count

        logger.info("预热字典数据...")
        count = _warmup_dict_data()
        logger.info(f"字典数据预热完成,共 {count} 条记录")
        total_count += count

        logger.info("预热权限数据...")
        count = _warmup_permission_data()
        logger.info(f"权限数据预热完成,共 {count} 条记录")
        total_count += count

        logger.info("预热角色数据...")
        count = _warmup_role_data()
        logger.info(f"角色数据预热完成,共 {count} 条记录")
        total_count += count

        logger.info("预热角色-主体关联...")
        count = _warmup_role_subject_data()
        logger.info(f"角色-主体关联预热完成,共 {count} 条缓存项")
        total_count += count

        logger.info("预热数据范围规则...")
        count = _warmup_data_scope_rule_data()
        logger.info(f"数据范围规则预热完成,共 {count} 条缓存项")
        total_count += count

        logger.info("预热组织节点...")
        count = _warmup_org_data()
        logger.info(f"组织节点预热完成,共 {count} 条缓存项")
        total_count += count

        logger.info("预热组织闭包表...")
        count = _warmup_org_closure_data()
        logger.info(f"组织闭包表预热完成,共 {count} 条缓存项")
        total_count += count

        logger.info("预热组织-主体关联...")
        count = _warmup_org_subject_data()
        logger.info(f"组织-主体关联预热完成,共 {count} 条缓存项")
        total_count += count

        logger.info("预热租户数据...")
        count = _warmup_tenant_data()
        logger.info(f"租户数据预热完成,共 {count} 条记录")
        total_count += count

        logger.info("预热用户数据...")
        count = _warmup_user_data()
        logger.info(f"用户数据预热完成,共 {count} 条记录")
        total_count += count

        logger.info("预热租户成员...")
        count = _warmup_member_data()
        logger.info(f"租户成员预热完成,共 {count} 条缓存项")
        total_count += count

        logger.info("预热账号绑定关系...")
        count = _warmup_account_bind_data()
        logger.info(f"账号绑定关系预热完成,共 {count} 条记录")
        total_count += count

        logger.info(f"缓存预热完成,共加载 {total_count} 条缓存记录")

    except Exception as e:
        logger.error(f"缓存预热失败: {str(e)}")
        raise
