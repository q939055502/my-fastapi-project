"""
权限初始化器

负责系统API权限资源的初始化

职责：
- 初始化平台级API权限资源（type=2）
- 创建API接口权限记录（路径、方法、场景等）
- 为后续角色权限分配提供基础数据

幂等性保证：
- 检查是否已存在API权限资源，若存在则跳过创建
- 重复执行不会产生重复数据
"""

from sqlalchemy import func, select

from src.core.constants import StatusConst
from src.core.log import logger
from src.core.storage import get_db


def init_permissions():
    """
    初始化系统API权限资源

    创建平台级API权限：
    - 平台管理API（scene=admin）
      - 租户管理、套餐管理、审计日志等
    - 通用业务API（scene=common）
      - 用户管理、角色管理、部门管理、资源管理等
    """
    logger.info("开始初始化系统API权限...")
    for session in get_db():
        from src.models.iam import Resource

        # 检查是否已存在API权限资源（type=2）
        result = session.execute(
            select(Resource).where(Resource.type == 2)
        )
        permissions = result.scalars().first()

        if not permissions:
            # 平台管理API权限
            admin_api_resources = [
                Resource(
                    code="admin_tenants_list",
                    name="平台租户列表",
                    type=2,  # API类型
                    parent_id=None,
                    api_path="/api/v1/admin/tenants/list",
                    api_method="GET",
                    sort=1,
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
                    scene="admin",
                    tenant_id=0,
                    is_system=True
                ),
            ]
            session.add_all(admin_api_resources)

            # 通用业务API权限
            common_api_resources = [
                # 用户管理API
                Resource(
                    code="user_list",
                    name="用户列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/users/list",
                    api_method="GET",
                    sort=1,
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                # 角色管理API
                Resource(
                    code="role_list",
                    name="角色列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/roles/list",
                    api_method="GET",
                    sort=1,
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                # 部门管理API
                Resource(
                    code="dept_list",
                    name="部门列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/depts/list",
                    api_method="GET",
                    sort=1,
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
                # 资源管理API
                Resource(
                    code="resource_list",
                    name="资源列表",
                    type=2,
                    parent_id=None,
                    api_path="/api/v1/resources/list",
                    api_method="GET",
                    sort=1,
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
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
                    status=StatusConst.ENABLED.value,
                    scene="common",
                    tenant_id=0,
                    is_system=True
                ),
            ]
            session.add_all(common_api_resources)

            session.commit()
            total_count = len(admin_api_resources) + len(common_api_resources)
            logger.info(f"系统API权限初始化成功 - 权限数量: {total_count}")
        else:
            count_result = session.execute(
                select(func.count(Resource.id)).where(Resource.type == 2)
            )
            permission_count = count_result.scalar()
            logger.info(f"系统API权限已存在，跳过初始化 - 当前权限数量: {permission_count}")
        break
