"""Base Service Class

Provides common functionality for all service classes, including:
- Transaction management
- Cache invalidation after write operations
- Common CRUD operations
"""

from typing import TypeVar

from src.common.core.storage.cache.cache_manager import cache_manager
from src.common.core.storage.transaction_manager import TransactionManager

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseService:
    """Base Service Class for all business services"""

    def __init__(self, repository):
        self.repository = repository
        self.transaction_manager = TransactionManager

    def _get_cache_prefix(self) -> str:
        """
        Get cache prefix for this service.

        Subclasses should override this method to provide a unique prefix.
        """
        return "base"

    def _invalidate_cache(self, *args) -> None:
        """Invalidate cache for given arguments"""
        prefix = self._get_cache_prefix()
        cache_manager.clear_pattern(f"{prefix}:{args[0]}:" if args else f"{prefix}:")

    def get(self, id: int, **kwargs) -> dict | None:
        """Get single item by ID"""
        with self.transaction_manager() as tm:
            obj = self.repository.get(id=id, session=tm.session, **kwargs)
            if obj:
                return obj.to_dict()
            return None

    def list(self, **kwargs) -> tuple[int, list[dict]]:
        """List items with pagination and filters"""
        with self.transaction_manager() as tm:
            total, items = self.repository.list(session=tm.session, **kwargs)
            return total, [item.to_dict() for item in items]

    def create(self, obj_in: CreateSchemaType) -> dict:
        """Create new item"""
        with self.transaction_manager() as tm:
            obj = self.repository.create(obj_in=obj_in, session=tm.session)
            tm.commit()

        self._invalidate_cache()
        return obj.to_dict()

    def update(self, id: int, obj_in: UpdateSchemaType) -> None:
        """Update existing item"""
        with self.transaction_manager() as tm:
            self.repository.update(id=id, obj_in=obj_in, session=tm.session)
            tm.commit()

        self._invalidate_cache(id)

    def delete(self, id: int) -> bool:
        """Delete item by ID"""
        with self.transaction_manager() as tm:
            success = self.repository.delete(id=id, session=tm.session)
            if success:
                tm.commit()

        if success:
            self._invalidate_cache(id)
        return success
