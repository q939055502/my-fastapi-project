"""
初始化器模块

统一管理应用启动时的所有初始化操作

使用方式：
```python
from src.initializers import run_all_initializers

run_all_initializers()
```

初始化顺序（保持幂等性）：
1. init_db() - 创建数据库表结构
2. 业务数据初始化（平台级 + 租户级）
3. 缓存预热 - 加载常用数据到缓存
"""

from src.core.log import logger


def run_all_initializers():
    """
    按顺序执行所有初始化器

    所有初始化函数都保持幂等性，重复执行不会产生重复数据或错误
    """
    logger.info("========== 开始执行系统初始化 ==========")

    # 数据库初始化（技术层）
    from src.core.storage.database import init_db

    # 缓存预热（技术层）
    from .cache_warmup_initializer import init_cache_warmup

    try:
        # 核心初始化
        init_db()

        # 业务数据初始化
        run_all_business_initializers()

        # 缓存预热（在业务数据初始化之后执行）
        # TODO: 暂时注释，待修复模型关系问题后再启用
        # init_cache_warmup()

        logger.info("========== 系统初始化完成 ==========")
    except Exception as e:
        logger.error(f"系统初始化失败: {str(e)}", exc_info=True)
        raise


def run_all_business_initializers():
    """按顺序执行所有业务数据初始化器

    所有初始化函数都保持幂等性，重复执行不会产生重复数据或错误
    """
    logger.info("========== 开始执行业务数据初始化 ==========")

    from .platform.config_initializer import init_system_config
    from .platform.dict_initializer import init_dict
    from .platform.menu_initializer import init_menus
    from .platform.org_initializer import init_orgs
    from .platform.permission_initializer import init_permissions
    from .platform.region_initializer import init_regions
    from .platform.role_initializer import init_roles
    from .platform.user_initializer import init_superuser
    from .tenant.tenant_dict_initializer import init_tenant_dict
    from .tenant.tenant_initializer import init_default_tenant, init_plans
    from .scheduler_initializer import init_scheduler

    try:
        # 核心初始化（已实现）
        init_superuser()
        init_plans()
        init_default_tenant()
        init_menus()
        init_permissions()
        init_roles()
        init_system_config()
        init_orgs()
        init_dict()

        # 扩展初始化（预留，暂未实现具体逻辑）
        init_tenant_dict()
        init_regions()

        # 定时任务初始化（在所有业务数据初始化完成后执行）
        init_scheduler()

        logger.info("========== 业务数据初始化完成 ==========")
    except Exception as e:
        logger.error(f"业务数据初始化失败: {str(e)}", exc_info=True)
        raise


def run_initializer(initializer_name: str):
    """
    单独执行指定的初始化器

    Args:
        initializer_name: 初始化器名称，可选值：
            - db: 数据库初始化
            - business: 执行业务数据初始化
            - cache_warmup: 缓存预热
            - cleanup_policy: 清理策略初始化（预留）
            - scheduler: 定时任务初始化（预留）
            - user: 用户初始化
            - tenant_plan: 租户套餐初始化
            - tenant_default: 默认租户初始化
            - menu: 菜单初始化
            - permission: 权限初始化
            - role: 角色初始化
            - config: 系统配置初始化
            - org: 组织初始化
            - dict: 字典初始化
            - tenant_dict: 租户字典初始化（预留）
            - region: 地区初始化（预留）
    """
    initializers = {
        "db": ("数据库初始化", lambda: __import__("src.core.storage.database", fromlist=["init_db"]).init_db()),
        "business": ("业务数据初始化", lambda: run_all_business_initializers()),
        "cache_warmup": ("缓存预热", lambda: __import__("src.initializers.cache_warmup_initializer", fromlist=["init_cache_warmup"]).init_cache_warmup()),
        "cleanup_policy": ("清理策略初始化", lambda: __import__("src.initializers.cleanup_policy_initializer", fromlist=["init_cleanup_policy"]).init_cleanup_policy()),
        "scheduler": ("定时任务初始化", lambda: __import__("src.initializers.scheduler_initializer", fromlist=["init_scheduler"]).init_scheduler()),
        "user": ("用户初始化", lambda: __import__("src.initializers.platform.user_initializer", fromlist=["init_superuser"]).init_superuser()),
        "tenant_plan": ("租户套餐初始化", lambda: __import__("src.initializers.tenant.tenant_initializer", fromlist=["init_plans"]).init_plans()),
        "tenant_default": ("默认租户初始化", lambda: __import__("src.initializers.tenant.tenant_initializer", fromlist=["init_default_tenant"]).init_default_tenant()),
        "menu": ("菜单初始化", lambda: __import__("src.initializers.platform.menu_initializer", fromlist=["init_menus"]).init_menus()),
        "permission": ("权限初始化", lambda: __import__("src.initializers.platform.permission_initializer", fromlist=["init_permissions"]).init_permissions()),
        "role": ("角色初始化", lambda: __import__("src.initializers.platform.role_initializer", fromlist=["init_roles"]).init_roles()),
        "config": ("系统配置初始化", lambda: __import__("src.initializers.platform.config_initializer", fromlist=["init_system_config"]).init_system_config()),
        "org": ("组织初始化", lambda: __import__("src.initializers.platform.org_initializer", fromlist=["init_orgs"]).init_orgs()),
        "dict": ("字典初始化", lambda: __import__("src.initializers.platform.dict_initializer", fromlist=["init_dict"]).init_dict()),
        "tenant_dict": ("租户字典初始化", lambda: __import__("src.initializers.tenant.tenant_dict_initializer", fromlist=["init_tenant_dict"]).init_tenant_dict()),
        "region": ("地区初始化", lambda: __import__("src.initializers.platform.region_initializer", fromlist=["init_regions"]).init_regions()),
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
    "run_all_business_initializers",
]