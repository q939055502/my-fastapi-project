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
from src.common.core.log import logger
from src.common.core.storage import get_db


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
        from src.models.platform import Permission

        # 检查是否已存在菜单资源（type=menu）
        result = session.execute(
            select(Permission).where(Permission.type == "menu")
        )
        menus = result.scalars().first()

        if not menus:
            # 创建父菜单
            parent_menu = Permission(
                name="系统管理",
                resource="system",
                action="access",
                scope="all",
                type="menu",
                parent_id=None,
                sort=1,
                is_system=True
            )
            session.add(parent_menu)
            session.flush()

            # 创建子菜单
            children_menu = [
                Permission(
                    name="用户管理",
                    resource="user",
                    action="access",
                    scope="all",
                    type="menu",
                    parent_id=parent_menu.id,
                    sort=1,
                    is_system=True
                ),
                Permission(
                    name="角色管理",
                    resource="role",
                    action="access",
                    scope="all",
                    type="menu",
                    parent_id=parent_menu.id,
                    sort=2,
                    is_system=True
                ),
                Permission(
                    name="菜单管理",
                    resource="menu",
                    action="access",
                    scope="all",
                    type="menu",
                    parent_id=parent_menu.id,
                    sort=3,
                    is_system=True
                ),
                Permission(
                    name="部门管理",
                    resource="dept",
                    action="access",
                    scope="all",
                    type="menu",
                    parent_id=parent_menu.id,
                    sort=4,
                    is_system=True
                ),
                Permission(
                    name="审计日志",
                    resource="auditlog",
                    action="access",
                    scope="all",
                    type="menu",
                    parent_id=parent_menu.id,
                    sort=5,
                    is_system=True
                ),
            ]
            session.add_all(children_menu)
            session.commit()
            logger.info("系统菜单初始化成功 - 菜单数量: 6")
        else:
            count_result = session.execute(
                select(func.count(Permission.id)).where(Permission.type == "menu")
            )
            menu_count = count_result.scalar()
            logger.info(f"系统菜单已存在，跳过初始化 - 当前菜单数量: {menu_count}")
        break
