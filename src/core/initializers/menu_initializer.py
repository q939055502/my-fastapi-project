"""
菜单初始化器

负责系统菜单资源的初始化

职责：
- 初始化平台级菜单结构（系统管理、用户管理、角色管理等）
- 创建菜单层级关系（父子菜单）
- 设置菜单图标、路径、排序等属性

幂等性保证：
- 检查是否已存在菜单资源，若存在则跳过创建
- 重复执行不会产生重复数据
"""

from sqlalchemy import func, select

from src.core.constants import StatusConst
from src.core.log import logger
from src.core.storage import get_db


def init_menus():
    """
    初始化系统菜单资源

    创建平台级菜单结构：
    - 系统管理（父菜单）
      - 用户管理
      - 角色管理
      - 菜单管理
      - 部门管理
      - 审计日志
    """
    logger.info("开始初始化系统菜单...")
    for session in get_db():
        from src.models.iam import Resource

        # 检查是否已存在菜单资源（type=1）
        result = session.execute(
            select(Resource).where(Resource.type == 1)
        )
        menus = result.scalars().first()

        if not menus:
            # 创建父菜单
            parent_menu = Resource(
                code="system",
                name="系统管理",
                type=1,  # 菜单类型
                parent_id=None,
                path="/system",
                icon="carbon:gui-management",
                sort=1,
                status=StatusConst.ENABLED.value,
                scene="superadmin",
                tenant_id=0,
                is_system=True
            )
            session.add(parent_menu)
            session.flush()

            # 创建子菜单
            children_menu = [
                Resource(
                    code="user",
                    name="用户管理",
                    type=1,
                    parent_id=parent_menu.id,
                    path="/system/user",
                    icon="material-symbols:person-outline-rounded",
                    sort=1,
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
                    scene="superadmin",
                    tenant_id=0,
                    is_system=True
                ),
            ]
            session.add_all(children_menu)
            session.commit()
            logger.info("系统菜单初始化成功 - 菜单数量: 6")
        else:
            count_result = session.execute(
                select(func.count(Resource.id)).where(Resource.type == 1)
            )
            menu_count = count_result.scalar()
            logger.info(f"系统菜单已存在，跳过初始化 - 当前菜单数量: {menu_count}")
        break
