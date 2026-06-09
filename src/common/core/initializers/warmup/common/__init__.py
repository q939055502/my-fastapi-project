"""通用预热模块"""
from .cache_warmup_initializer import init_cache_warmup
from .scheduler_initializer import init_scheduler
from .cleanup_policy_initializer import init_cleanup_policy

__all__ = [
    "init_cache_warmup",
    "init_scheduler",
    "init_cleanup_policy",
]
