"""Storage module

Provides database connection, cache management and transaction management.

Core components:
- database: SQLAlchemy database connection configuration
- cache: Three-level cache system (L1 local memory + L2 Redis + L3 database)
- transaction_manager: Transaction manager
- repository_base: Base repository class for CRUD operations
"""

from .cache import CacheManager, cache_manager
from .database import Base, SessionLocal, close_db, engine, get_db, init_db
from .repository_base import BaseRepository
from .transaction_manager import TransactionManager, get_transaction_manager

__all__ = [
    "Base",
    "BaseRepository",
    "CacheManager",
    "SessionLocal",
    "TransactionManager",
    "cache_manager",
    "close_db",
    "engine",
    "get_db",
    "get_transaction_manager",
    "init_db",
]
