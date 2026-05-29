"""
存储模块导出

包含数据库、Redis缓存、文件存储等核心存储组件
"""
from .database import (
    Base,
    SessionLocal,
    close_db,
    engine,
    get_db,
)
from .database import (
    init_db as init_database,
)
from .file_storage import StorageBackend, get_storage_backend, storage
from .generic_repository import GenericRepository
from .redis import cache_manager, cached, clear_role_cache, clear_user_cache
from .unit_of_work import UnitOfWork, get_unit_of_work

__all__ = [
    "Base",
    "engine",
    "SessionLocal",
    "get_db",
    "init_database",
    "close_db",
    "cache_manager",
    "cached",
    "clear_user_cache",
    "clear_role_cache",
    "storage",
    "get_storage_backend",
    "StorageBackend",
    "GenericRepository",
    "UnitOfWork",
    "get_unit_of_work",
]
