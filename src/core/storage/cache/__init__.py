"""Cache module exports

缓存层对外导出的接口。

核心组件：
- CacheManager: 统一缓存管理器（L1+L2 二级缓存）
- cache_manager: 全局单例
- CacheType: 缓存类型枚举
- build_cache_key: 缓存键构建器
- register_cache_events: 注册 ORM 事件缓存联动
"""

from .cache_key import CacheType, build_cache_key
from .cache_manager import CacheManager, cache_manager, clear_user_cache

__all__ = [
    "CacheType",
    "build_cache_key",
    "CacheManager",
    "cache_manager",
    "clear_user_cache",
]
