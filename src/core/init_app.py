
"""
数据初始化模块

本模块包含应用启动时的数据初始化函数：
- 数据库表结构创建
- 超级管理员用户创建
- 系统资源（菜单/API/按钮）创建
- 角色及权限分配

在 src/__init__.py 的 lifespan 调用
"""

from sqlalchemy import func, or_
from sqlalchemy import select

from src.core.config import settings
from src.core.log import logger
from src.core.storage import engine, Base, get_db
# Import all models to register them with Base.metadata
import src.models


def init_db():
    """
    创建数据库表结构

    使用 SQLAlchemy 的 Base.metadata.create_all() 根据模型定义
    自动创建所有表（如果不存在）
    """
    logger.info("开始数据库表结构创建...")
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表结构创建完成")


def init_superuser():
    """
    初始化超级管理员用户和普通测试用户

    检查是否已存在超级管理员用户，若不存在则创建默认超级管理员：
    - 用户名: superadmin
    - 邮箱: superadmin@superadmin.com
    - 密码: qaz123456

    同时创建普通测试用户：
    - 用户名: user1
    - 邮箱: user1@example.com
    - 密码: qaz123456

    - 用户名: user2
    - 邮箱: user2@example.com
    - 密码: qaz123456

    权限通过角色来管理，不再使用is_superuser字段
    """
    logger.info("开始初始化超级管理员用户...")
    for session in get_db():
        try:
            from src.repositories.sys.user_repository import user_repository
            from src.repositories.sys.user_repository import UserCreate
            
            result = session.execute(select(user_repository.model))
            user = result.scalars().first()
            if not user:
                user_repository.create_user(
                    UserCreate(
                        username="superadmin",
                        email="superadmin@superadmin.com",
                        password=settings.SUPER_ADMIN_PASSWORD,
                        is_active=True,
                    ),
                    session=session,
                )
                session.commit()
                logger.info("超级管理员用户创建成功 - 用户名: superadmin")
            else:
                logger.info("超级管理员用户已存在，跳过创建")

            user1_result = session.execute(
                select(user_repository.model).where(user_repository.model.username == "user1")
            )
            user1 = user1_result.scalars().first()
            if not user1:
                user_repository.create_user(
                    UserCreate(
                        username="user1",
                        email="user1@example.com",
                        password="qaz123456",
                        is_active=True,
                    ),
                    session=session,
                )
                session.commit()
                logger.info("普通测试用户创建成功 - 用户名: user1")
            else:
                logger.info("普通测试用户已存在，跳过创建")

            user2_result = session.execute(
                select(user_repository.model).where(user_repository.model.username == "user2")
            )
            user2 = user2_result.scalars().first()
            if not user2:
                user_repository.create_user(
                    UserCreate(
                        username="user2",
                        email="user2@example.com",
                        password="qaz123456",
                        is_active=True,
                    ),
                    session=session,
                )
                session.commit()
                logger.info("普通测试用户创建成功 - 用户名: user2")
            else:
                logger.info("普通测试用户已存在，跳过创建")
        except Exception as e:
            session.rollback()
            logger.error(f"初始化用户失败: {str(e)}")
            raise
        break


def init_plans():
    """
    初始化租户套餐

    创建默认的租户套餐：
    - 免费版（自动通过，限5个用户）
    - 基础版（自动通过，限20个用户）
    - 专业版（人工审核，限100个用户）
    - 企业版（人工审核，无用户限制）
    """
    logger.info("开始初始化租户套餐...")
    for session in get_db():
        from src.models.sys.tenant import TenantPlan
        result = session.execute(select(TenantPlan))
        plans = result.scalars().first()
        if not plans:
            default_plans = [
                TenantPlan(
                    name="免费版",
                    code="free",
                    is_auto_approve=1,
                    max_users=5,
                    max_depts=3,
                    max_storage=1024,
                    max_file_size=10,
                    price=0,
                    features="基础功能",
                    available_modules="user,dept",
                    status=1,
                    sort=1
                ),
                TenantPlan(
                    name="基础版",
                    code="basic",
                    is_auto_approve=1,
                    max_users=20,
                    max_depts=10,
                    max_storage=10240,
                    max_file_size=50,
                    price=9900,
                    features="标准功能",
                    available_modules="user,dept,dict",
                    status=1,
                    sort=2
                ),
                TenantPlan(
                    name="专业版",
                    code="professional",
                    is_auto_approve=0,
                    max_users=100,
                    max_depts=50,
                    max_storage=102400,
                    max_file_size=100,
                    price=29900,
                    features="高级功能",
                    available_modules="user,dept,dict,file",
                    status=1,
                    sort=3
                ),
                TenantPlan(
                    name="企业版",
                    code="enterprise",
                    is_auto_approve=0,
                    max_users=None,
                    max_depts=None,
                    max_storage=1048576,
                    max_file_size=500,
                    price=99900,
                    features="企业级功能",
                    available_modules="user,dept,dict,file,log",
                    status=1,
                    sort=4
                ),
            ]
            session.add_all(default_plans)
            session.commit()
            logger.info("租户套餐初始化成功 - 套餐数量: 4")
        else:
            count_result = session.execute(select(func.count(TenantPlan.id)))
            plan_count = count_result.scalar()
            logger.info(f"租户套餐已存在，跳过初始化 - 当前套餐数量: {plan_count}")
        break


def init_default_tenant():
    """
    初始化默认租户

    创建一个默认业务租户，并将 user1 设为其户主：
    - 租户名称: 默认租户
    - 租户编码: default
    - 套餐: 免费版
    - 户主: user1
    """
    logger.info("开始初始化默认租户...")
    for session in get_db():
        try:
            from src.models.sys.tenant import Tenant
            from src.repositories.sys.user_repository import user_repository
            from src.models.sys.associations import user_tenant_association
            
            result = session.execute(select(Tenant).where(Tenant.code == "default"))
            default_tenant = result.scalars().first()
            
            if not default_tenant:
                user1_result = session.execute(
                    select(user_repository.model).where(user_repository.model.username == "user1")
                )
                user1 = user1_result.scalars().first()
                
                if user1:
                    default_tenant = Tenant(
                        name="默认租户",
                        code="default",
                        plan_id=1,
                        owner_user_id=user1.id,
                        status="active"
                    )
                    session.add(default_tenant)
                    session.flush()
                    
                    session.execute(
                        user_tenant_association.insert().values(
                            user_id=user1.id,
                            tenant_id=default_tenant.id,
                            is_owner=True
                        )
                    )
                    
                    session.commit()
                    logger.info(f"默认租户创建成功 - 租户ID: {default_tenant.id}, 户主: user1")
                else:
                    logger.warning("user1 用户不存在，跳过创建默认租户")
            else:
                logger.info("默认租户已存在，跳过创建")
        except Exception as e:
            session.rollback()
            logger.error(f"初始化默认租户失败: {str(e)}")
            raise
        break


def init_resources():
    """
    初始化系统资源（菜单/API/按钮）

    创建统一的资源记录，包含菜单、API接口、按钮
    """
    logger.info("开始初始化系统资源...")
    for session in get_db():
        from src.models.sys.resource import Resource
        result = session.execute(select(Resource))
        resources = result.scalars().first()
        if not resources:
            # 1. 创建菜单
            parent_menu = Resource(
                code="system",
                name="系统管理",
                type=1,
                parent_id=None,
                path="/system",
                icon="carbon:gui-management",
                sort=1,
                status=1,
                scene="superadmin",
                tenant_id=0,
                is_system=True
            )
            session.add(parent_menu)
            session.flush()

            children_menu = [
                Resource(
                    code="user",
                    name="用户管理",
                    type=1,
                    parent_id=parent_menu.id,
                    path="/system/user",
                    icon="material-symbols:person-outline-rounded",
                    sort=1,
                    status=1,
                    scene="superadmin",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="role",
                    name="角色管理",
                    type=1,
                    parent_id=parent_menu.id,
                    path="/system/role",
                    icon="carbon:user-role",
                    sort=2,
                    status=1,
                    scene="superadmin",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="menu",
                    name="菜单管理",
                    type=1,
                    parent_id=parent_menu.id,
                    path="/system/menu",
                    icon="material-symbols:list-alt-outline",
                    sort=3,
                    status=1,
                    scene="superadmin",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="dept",
                    name="部门管理",
                    type=1,
                    parent_id=parent_menu.id,
                    path="/system/dept",
                    icon="mingcute:department-line",
                    sort=4,
                    status=1,
                    scene="superadmin",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="auditlog",
                    name="审计日志",
                    type=1,
                    parent_id=parent_menu.id,
                    path="/system/auditlog",
                    icon="ph:clipboard-text-bold",
                    sort=5,
                    status=1,
                    scene="superadmin",
                    tenant_id=0,
                    is_system=True
                ),
            ]
            session.add_all(children_menu)

            # 2. 创建平台超管专属API资源
            admin_api_resources = [
                Resource(
                    code="admin_tenants_list",
                    name="平台租户列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/admin/tenants/list",
                    api_method="GET",
                    sort=1,
                    status=1,
                    scene="admin",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="admin_tenants_create",
                    name="平台创建租户",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/admin/tenants",
                    api_method="POST",
                    sort=2,
                    status=1,
                    scene="admin",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="admin_plans_list",
                    name="平台套餐列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/admin/plans/list",
                    api_method="GET",
                    sort=3,
                    status=1,
                    scene="admin",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="admin_auditlog",
                    name="平台审计日志",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/admin/auditlog",
                    api_method="GET",
                    sort=4,
                    status=1,
                    scene="admin",
                    tenant_id=0,
                    is_system=True
                ),
            ]
            session.add_all(admin_api_resources)
            
            # 3. 创建通用API资源（所有角色）
            common_api_resources = [
                Resource(
                    code="user_list",
                    name="用户列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/users/list",
                    api_method="GET",
                    sort=1,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="user_create",
                    name="创建用户",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/users",
                    api_method="POST",
                    sort=2,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="user_update",
                    name="更新用户",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/users/{user_id}",
                    api_method="PUT",
                    sort=3,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="user_delete",
                    name="删除用户",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/users/{user_id}",
                    api_method="DELETE",
                    sort=4,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="role_list",
                    name="角色列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/roles/list",
                    api_method="GET",
                    sort=1,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="role_create",
                    name="创建角色",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/roles",
                    api_method="POST",
                    sort=2,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="role_update",
                    name="更新角色",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/roles/{role_id}",
                    api_method="PUT",
                    sort=3,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="role_delete",
                    name="删除角色",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/roles/{role_id}",
                    api_method="DELETE",
                    sort=4,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="dept_list",
                    name="部门列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/depts/list",
                    api_method="GET",
                    sort=1,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="dept_create",
                    name="创建部门",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/depts",
                    api_method="POST",
                    sort=2,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="dept_update",
                    name="更新部门",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/depts/{dept_id}",
                    api_method="PUT",
                    sort=3,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="dept_delete",
                    name="删除部门",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/depts/{dept_id}",
                    api_method="DELETE",
                    sort=4,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="resource_list",
                    name="资源列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/resources/list",
                    api_method="GET",
                    sort=1,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="resource_create",
                    name="创建资源",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/resources",
                    api_method="POST",
                    sort=2,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="resource_update",
                    name="更新资源",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/resources/{resource_id}",
                    api_method="PUT",
                    sort=3,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                Resource(
                    code="resource_delete",
                    name="删除资源",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/resources/{resource_id}",
                    api_method="DELETE",
                    sort=4,
                    status=1,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
            ]
            session.add_all(common_api_resources)

            session.commit()
            logger.info("系统资源初始化成功")
        else:
            count_result = session.execute(select(func.count(Resource.id)))
            resource_count = count_result.scalar()
            logger.info(f"系统资源已存在，跳过初始化 - 当前资源数量: {resource_count}")
        break


def init_roles():
    """
    初始化平台角色体系

    创建系统内置平台角色（tenant_id=0, is_system=True）：
    1. 平台超级管理员 - 全平台最高权限，跨所有租户无限制
    2. 平台运营管理员 - 租户全生命周期管理
    3. 平台财务管理员 - 仅账单、订单、充值、续费、发票、欠费管控
    4. 平台审核管理员 - 企业资质审核、资料审核、内容风控
    5. 平台运维专员 - 日志查看、系统状态监控、简单问题排查
    6. 平台客服专员 - 查看租户基础信息、工单处理、协助改基础资料
    """
    logger.info("开始初始化平台角色...")
    for session in get_db():
        from src.models.sys.role import Role
        from src.models.sys.resource import Resource
        from src.models.sys.associations import role_resource_association
        from src.models.sys.associations import user_role_association
        from src.models.sys.user import User
        from src.repositories.sys.user_repository import user_repository
        
        result = session.execute(select(Role))
        roles = result.scalars().first()
        if not roles:
            # 平台角色列表
            platform_roles = [
                Role(
                    name="平台超级管理员",
                    remark="全平台最高权限，跨所有租户无限制，可管理所有租户、可操作回收站、可物理硬删",
                    tenant_id=0,
                    is_system=True
                ),
                Role(
                    name="平台运营管理员",
                    remark="租户全生命周期管理，审核租户入驻、信息修改，查看租户基础信息、账号数量，冻结违规租户，分配租户套餐、配置",
                    tenant_id=0,
                    is_system=True
                ),
                Role(
                    name="平台财务管理员",
                    remark="仅账单、订单、充值、续费、发票、欠费管控，无权查看员工业务数据、无权冻结租户",
                    tenant_id=0,
                    is_system=True
                ),
                Role(
                    name="平台审核管理员",
                    remark="企业资质审核、资料审核、内容风控，无任何账号与租户管理权限",
                    tenant_id=0,
                    is_system=True
                ),
                Role(
                    name="平台运维专员",
                    remark="日志查看、系统状态监控、简单问题排查，仅查看，无任何修改删除权限",
                    tenant_id=0,
                    is_system=True
                ),
                Role(
                    name="平台客服专员",
                    remark="查看租户基础信息、工单处理、协助改基础资料，无权查看隐私数据、无权改权限",
                    tenant_id=0,
                    is_system=True
                ),
                Role(
                    name="平台普通用户",
                    remark="平台基础用户，仅能查看个人信息和基础功能，无管理权限",
                    tenant_id=0,
                    is_system=True
                ),
            ]
            session.add_all(platform_roles)
            session.flush()

            # 获取平台超级管理员角色
            superadmin_role_result = session.execute(
                select(Role).where(Role.name == "平台超级管理员")
            )
            superadmin_role = superadmin_role_result.scalars().first()

            if superadmin_role:
                # 获取所有资源
                all_resources_result = session.execute(select(Resource))
                all_resources = all_resources_result.scalars().all()

                # 平台超级管理员角色：分配所有资源
                for resource in all_resources:
                    session.execute(
                        role_resource_association.insert().values(
                            role_id=superadmin_role.id,
                            resource_id=resource.id
                        )
                    )

                # 给 superadmin 用户分配平台超级管理员角色
                superadmin_user = session.execute(
                    select(User).where(User.username == "superadmin")
                ).scalars().first()

                if superadmin_user:
                    session.execute(
                        user_role_association.insert().values(
                            user_id=superadmin_user.id,
                            role_id=superadmin_role.id
                        )
                    )
                    logger.info(f"已为超级管理员用户分配平台超级管理员角色 - 用户ID: {superadmin_user.id}")

            session.commit()
            logger.info("平台角色初始化成功 - 共创建 6 个平台角色")
        else:
            count_result = session.execute(select(func.count(Role.id)))
            role_count = count_result.scalar()
            logger.info(f"平台角色已存在，跳过创建 - 当前角色数量: {role_count}")
            
            superadmin_role_result = session.execute(
                select(Role).where(Role.name == "平台超级管理员")
            )
            superadmin_role = superadmin_role_result.scalars().first()
            
            if superadmin_role:
                superadmin_user = session.execute(
                    select(User).where(User.username == "superadmin")
                ).scalars().first()
                
                if superadmin_user:
                    existing_association = session.execute(
                        user_role_association.select().where(
                            user_role_association.c.user_id == superadmin_user.id,
                            user_role_association.c.role_id == superadmin_role.id
                        )
                    ).first()
                    
                    if not existing_association:
                        session.execute(
                            user_role_association.insert().values(
                                user_id=superadmin_user.id,
                                role_id=superadmin_role.id
                            )
                        )
                        session.commit()
                        logger.info(f"已为超级管理员用户绑定平台超级管理员角色")
        break


def init_system_config():
    """
    初始化系统配置项

    创建平台全局配置项，包括：
    - 系统名称、logo
    - 邮件配置
    - 存储配置
    - 安全配置
    """
    logger.info("开始初始化系统配置...")
    for session in get_db():
        try:
            from src.models.sys.system_config import SystemConfig
            count_result = session.execute(select(func.count(SystemConfig.id)))
            config_count = count_result.scalar()
            
            if config_count == 0:
                configs = [
                    SystemConfig(
                        name="系统名称",
                        code="system.name",
                        value="房屋鉴定管理系统",
                        type="string",
                        group="system",
                        sort=1,
                        remark="平台显示名称"
                    ),
                    SystemConfig(
                        name="系统Logo",
                        code="system.logo",
                        value="",
                        type="string",
                        group="system",
                        sort=2,
                        remark="平台Logo URL"
                    ),
                    SystemConfig(
                        name="系统描述",
                        code="system.description",
                        value="企业级FastAPI后端项目",
                        type="string",
                        group="system",
                        sort=3,
                        remark="平台描述信息"
                    ),
                    SystemConfig(
                        name="是否启用注册",
                        code="system.allow_register",
                        value="true",
                        type="boolean",
                        group="system",
                        sort=4,
                        remark="是否允许用户注册"
                    ),
                    SystemConfig(
                        name="是否启用验证码",
                        code="system.enable_captcha",
                        value="false",
                        type="boolean",
                        group="system",
                        sort=5,
                        remark="是否启用登录验证码"
                    ),
                    SystemConfig(
                        name="会话超时时间",
                        code="system.session_timeout",
                        value="1440",
                        type="int",
                        group="system",
                        sort=6,
                        remark="会话超时时间（分钟）"
                    ),
                    SystemConfig(
                        name="邮件服务器地址",
                        code="mail.host",
                        value="smtp.example.com",
                        type="string",
                        group="mail",
                        sort=1,
                        remark="SMTP服务器地址"
                    ),
                    SystemConfig(
                        name="邮件服务器端口",
                        code="mail.port",
                        value="587",
                        type="int",
                        group="mail",
                        sort=2,
                        remark="SMTP端口"
                    ),
                    SystemConfig(
                        name="邮件用户名",
                        code="mail.username",
                        value="",
                        type="string",
                        group="mail",
                        sort=3,
                        remark="SMTP用户名"
                    ),
                    SystemConfig(
                        name="邮件密码",
                        code="mail.password",
                        value="",
                        type="string",
                        group="mail",
                        sort=4,
                        remark="SMTP密码"
                    ),
                    SystemConfig(
                        name="邮件发件人",
                        code="mail.sender",
                        value="",
                        type="string",
                        group="mail",
                        sort=5,
                        remark="发件人邮箱"
                    ),
                ]
                
                session.add_all(configs)
                session.commit()
                logger.info(f"系统配置初始化成功 - 配置项数量: {len(configs)}")
            else:
                logger.info(f"系统配置已存在，跳过初始化 - 当前配置数量: {config_count}")
        except Exception as e:
            session.rollback()
            logger.error(f"初始化系统配置失败: {str(e)}")
            raise
        break


def init_depts():
    """
    初始化部门数据

    创建系统默认部门结构
    """
    logger.info("开始初始化部门数据...")
    for session in get_db():
        try:
            from src.models.sys.dept import Dept
            count_result = session.execute(select(func.count(Dept.id)))
            dept_count = count_result.scalar()
            
            if dept_count == 0:
                depts = [
                    Dept(
                        name="总公司",
                        code="root",
                        tenant_id=None,
                        parent_id=None,
                        level=1,
                        path="/1/",
                        sort=1,
                        leader="超级管理员",
                        remark="系统根部门"
                    ),
                    Dept(
                        name="技术部",
                        code="tech",
                        tenant_id=None,
                        parent_id=1,
                        level=2,
                        path="/1/2/",
                        sort=1,
                        leader="技术主管",
                        remark="技术研发部门"
                    ),
                    Dept(
                        name="产品部",
                        code="product",
                        tenant_id=None,
                        parent_id=1,
                        level=2,
                        path="/1/3/",
                        sort=2,
                        leader="产品经理",
                        remark="产品管理部门"
                    ),
                    Dept(
                        name="运营部",
                        code="operation",
                        tenant_id=None,
                        parent_id=1,
                        level=2,
                        path="/1/4/",
                        sort=3,
                        leader="运营主管",
                        remark="运营管理部门"
                    ),
                    Dept(
                        name="前端开发组",
                        code="frontend",
                        tenant_id=None,
                        parent_id=2,
                        level=3,
                        path="/1/2/5/",
                        sort=1,
                        remark="前端开发小组"
                    ),
                    Dept(
                        name="后端开发组",
                        code="backend",
                        tenant_id=None,
                        parent_id=2,
                        level=3,
                        path="/1/2/6/",
                        sort=2,
                        remark="后端开发小组"
                    ),
                ]
                
                session.add_all(depts)
                session.commit()
                logger.info(f"部门数据初始化成功 - 部门数量: {len(depts)}")
            else:
                logger.info(f"部门数据已存在，跳过初始化 - 当前部门数量: {dept_count}")
        except Exception as e:
            session.rollback()
            logger.error(f"初始化部门数据失败: {str(e)}")
            raise
        break


def init_data():
    """
    数据初始化入口函数

    按顺序调用所有初始化函数：
    1. init_db() - 创建数据库表结构
    2. init_superuser() - 创建超级管理员用户和普通测试用户（superadmin, user1, user2）
    3. init_plans() - 创建租户套餐
    4. init_default_tenant() - 创建默认租户（user1 为户主）
    5. init_resources() - 创建系统资源（菜单/API/按钮）
    6. init_roles() - 创建角色并分配权限

    所有初始化函数都具有幂等性，已存在的数据会被跳过
    """
    logger.info("系统初始化开始...")

    logger.info("开始数据库初始化和迁移...")
    init_db()
    logger.info("数据库初始化完成")

    init_superuser()
    init_plans()
    init_default_tenant()
    init_resources()
    init_roles()
    init_system_config()
    init_depts()

    logger.info("系统初始化完成！")

