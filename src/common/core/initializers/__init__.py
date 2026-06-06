"""
初始化器模块

统一管理应用启动时的所有初始化操作

使用方式：
```python
from src.common.core.initializers import run_all_initializers

run_all_initializers()
```

初始化顺序（保持幂等性）：
1. init_db() - 创建数据库表结构
2. init_superuser() - 创建超级管理员和测试用户
3. init_plans() - 创建租户套餐
4. init_default_tenant() - 创建默认租户
5. init_menus() - 创建系统菜单资源
6. init_permissions() - 创建系统API权限资源
7. init_roles() - 创建平台角色并分配权限
8. init_system_config() - 创建系统配置项
9. init_depts() - 创建系统部门
10. init_dict() - 创建系统字典数据
11. init_scheduler() - 初始化定时任务（预留）
12. init_tenant_dict() - 初始化租户默认字典（预留）
13. init_regions() - 初始化省市区数据（预留）
14. init_cleanup_policy() - 初始化数据清理策略（预留）
15. init_cache_warmup() - 缓存预热（预留）
"""

from src.common.core.log import logger


def run_all_initializers():
    """
    按顺序执行所有初始化器

    所有初始化函数都保持幂等性，重复执行不会产生重复数据或错误
    """
    logger.info("========== 开始执行系统初始化 ==========")

    # 预留扩展点（暂未实现）
    from .common.cache_warmup_initializer import init_cache_warmup
    from .common.cleanup_policy_initializer import init_cleanup_policy
    from .common.db_initializer import init_db
    from .common.scheduler_initializer import init_scheduler
    from .platform.config_initializer import init_system_config
    from .platform.dept_initializer import init_depts
    from .platform.dict_initializer import init_dict
    from .platform.menu_initializer import init_menus
    from .platform.permission_initializer import init_permissions
    from .platform.region_initializer import init_regions
    from .platform.role_initializer import init_roles
    from .platform.user_initializer import init_superuser
    from .tenant.tenant_dict_initializer import init_tenant_dict
    from .tenant.tenant_initializer import init_default_tenant, init_plans

    try:
        # 核心初始化（已实现）
        init_db()
        init_superuser()
        init_plans()
        init_default_tenant()
        init_menus()
        init_permissions()
        init_roles()
        init_system_config()
        init_depts()
        init_dict()

        # 扩展初始化（预留，暂未实现具体逻辑）
        init_scheduler()
        init_tenant_dict()
        init_regions()
        init_cleanup_policy()
        init_cache_warmup()

        logger.info("========== 系统初始化完成 ==========")
    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}", exc_info=True)
        raise


def run_initializer(initializer_name: str):
    """
    单独执行指定的初始化器

    Args:
        initializer_name: 初始化器名称，可选值：
            - db: 数据库初始化
            - user: 用户初始化
            - tenant_plan: 租户套餐初始化
            - tenant_default: 默认租户初始化
            - menu: 菜单初始化
            - permission: 权限初始化
            - role: 角色初始化
            - config: 系统配置初始化
            - dept: 部门初始化
            - dict: 字典初始化
            - scheduler: 定时任务初始化（预留）
            - tenant_dict: 租户字典初始化（预留）
            - region: 地区初始化（预留）
            - cleanup_policy: 清理策略初始化（预留）
            - cache_warmup: 缓存预热（预留）
    """
    initializers = {
        "db": ("数据库初始化", lambda: __import__("src.common.core.initializers.common.db_initializer", fromlist=["init_db"]).init_db()),
        "user": ("用户初始化", lambda: __import__("src.common.core.initializers.platform.user_initializer", fromlist=["init_superuser"]).init_superuser()),
        "tenant_plan": ("租户套餐初始化", lambda: __import__("src.common.core.initializers.tenant.tenant_initializer", fromlist=["init_plans"]).init_plans()),
        "tenant_default": ("默认租户初始化", lambda: __import__("src.common.core.initializers.tenant.tenant_initializer", fromlist=["init_default_tenant"]).init_default_tenant()),
        "menu": ("菜单初始化", lambda: __import__("src.common.core.initializers.platform.menu_initializer", fromlist=["init_menus"]).init_menus()),
        "permission": ("权限初始化", lambda: __import__("src.common.core.initializers.platform.permission_initializer", fromlist=["init_permissions"]).init_permissions()),
        "role": ("角色初始化", lambda: __import__("src.common.core.initializers.platform.role_initializer", fromlist=["init_roles"]).init_roles()),
        "config": ("系统配置初始化", lambda: __import__("src.common.core.initializers.platform.config_initializer", fromlist=["init_system_config"]).init_system_config()),
        "dept": ("部门初始化", lambda: __import__("src.common.core.initializers.platform.dept_initializer", fromlist=["init_depts"]).init_depts()),
        "dict": ("字典初始化", lambda: __import__("src.common.core.initializers.platform.dict_initializer", fromlist=["init_dict"]).init_dict()),
        "scheduler": ("定时任务初始化", lambda: __import__("src.common.core.initializers.common.scheduler_initializer", fromlist=["init_scheduler"]).init_scheduler()),
        "tenant_dict": ("租户字典初始化", lambda: __import__("src.common.core.initializers.tenant.tenant_dict_initializer", fromlist=["init_tenant_dict"]).init_tenant_dict()),
        "region": ("地区初始化", lambda: __import__("src.common.core.initializers.platform.region_initializer", fromlist=["init_regions"]).init_regions()),
        "cleanup_policy": ("清理策略初始化", lambda: __import__("src.common.core.initializers.common.cleanup_policy_initializer", fromlist=["init_cleanup_policy"]).init_cleanup_policy()),
        "cache_warmup": ("缓存预热", lambda: __import__("src.common.core.initializers.common.cache_warmup_initializer", fromlist=["init_cache_warmup"]).init_cache_warmup()),
    }

    if initializer_name not in initializers:
        raise ValueError(f"未知的初始化器: {initializer_name}，可选值: {list(initializers.keys())}")

    name, func = initializers[initializer_name]
    logger.info(f"开始执行: {name}")
    func()
    logger.info(f"完成: {name}")


__all__ = [
    "run_all_initializers",
    "run_initializer",
]
