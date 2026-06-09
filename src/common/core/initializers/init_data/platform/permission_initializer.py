"""
权限初始化器

负责系统API权限资源的初始化

职责：
- 初始化平台级API权限（type=api）
- 为后续角色权限分配提供基础数据

幂等性保证：
- 检查是否已存在API权限，若存在则跳过创建
- 重复执行不会产生重复数据
"""

from sqlalchemy import func, select
from src.common.core.log import logger
from src.common.core.storage import get_db


def init_permissions():
    """
    初始化系统API权限

    创建平台级API权限：
    - 用户管理、角色管理、部门管理、权限管理等
    """
    logger.info("开始初始化系统API权限...")
    for session in get_db():
        from src.models.platform import Permission

        # 检查是否已存在API权限
        result = session.execute(
            select(Permission).where(Permission.type == "api")
        )
        permissions = result.scalars().first()

        if not permissions:
            # API权限列表
            api_permissions = [
                # 用户管理API
                Permission(resource="user", action="list", scope="all", name="用户列表", type="api", sort=1, is_system=True),
                Permission(resource="user", action="create", scope="all", name="创建用户", type="api", sort=2, is_system=True),
                Permission(resource="user", action="update", scope="all", name="更新用户", type="api", sort=3, is_system=True),
                Permission(resource="user", action="delete", scope="all", name="删除用户", type="api", sort=4, is_system=True),
                # 角色管理API
                Permission(resource="role", action="list", scope="all", name="角色列表", type="api", sort=1, is_system=True),
                Permission(resource="role", action="create", scope="all", name="创建角色", type="api", sort=2, is_system=True),
                Permission(resource="role", action="update", scope="all", name="更新角色", type="api", sort=3, is_system=True),
                Permission(resource="role", action="delete", scope="all", name="删除角色", type="api", sort=4, is_system=True),
                # 部门管理API
                Permission(resource="dept", action="list", scope="all", name="部门列表", type="api", sort=1, is_system=True),
                Permission(resource="dept", action="create", scope="all", name="创建部门", type="api", sort=2, is_system=True),
                Permission(resource="dept", action="update", scope="all", name="更新部门", type="api", sort=3, is_system=True),
                Permission(resource="dept", action="delete", scope="all", name="删除部门", type="api", sort=4, is_system=True),
                # 权限管理API
                Permission(resource="permission", action="list", scope="all", name="权限列表", type="api", sort=1, is_system=True),
                Permission(resource="permission", action="create", scope="all", name="创建权限", type="api", sort=2, is_system=True),
                Permission(resource="permission", action="update", scope="all", name="更新权限", type="api", sort=3, is_system=True),
                Permission(resource="permission", action="delete", scope="all", name="删除权限", type="api", sort=4, is_system=True),
            ]
            session.add_all(api_permissions)
            session.commit()
            logger.info(f"系统API权限初始化成功 - 权限数量: {len(api_permissions)}")
        else:
            count_result = session.execute(
                select(func.count(Permission.id)).where(Permission.type == "api")
            )
            permission_count = count_result.scalar()
            logger.info(f"系统API权限已存在，跳过初始化 - 当前权限数量: {permission_count}")
        break
