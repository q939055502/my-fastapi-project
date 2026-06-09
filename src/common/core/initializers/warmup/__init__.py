"""缓存预热模块"""
from .common.cache_warmup_initializer import init_cache_warmup
from .common.scheduler_initializer import init_scheduler
from .common.cleanup_policy_initializer import init_cleanup_policy

__all__ = [
    "init_cache_warmup",
    "init_scheduler",
    "init_cleanup_policy",
]
