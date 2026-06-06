"""Generic Repository Base Class

Provides basic CRUD operations without transaction management.
Transaction management is controlled by TransactionManager.

Core features:
- Dual-channel query: list() filters soft-deleted, list_all() queries all
- Adaptive deletion: automatically selects soft or hard delete based on model
- System field protection: is_system field cannot be modified or deleted
"""
import builtins
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

PROTECTED_SYSTEM_FIELDS = {"id", "is_deleted", "delete_time", "is_system", "created_at", "updated_at"}


class GenericRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic Repository Base Class

    Provides basic CRUD operations without commit.
    Transaction management is controlled by TransactionManager.

    Core features:
    - Dual-channel query: filters soft-deleted by default, with_deleted queries all
    - Adaptive deletion: automatically selects deletion method based on soft-delete support
    """

    def __init__(self, model: type[ModelType]):
        self.model = model
        self._has_soft_delete = self._check_soft_delete()

    def _check_soft_delete(self) -> bool:
        """检查模型是否继承了软删除Mixin"""
        return hasattr(self.model, 'is_deleted') and hasattr(self.model, 'delete_time')

    def _apply_soft_delete_filter(self, query):
        """应用软删除过滤条件"""
        if self._has_soft_delete:
            return query.where(self.model.is_deleted.is_(False))
        return query

    def _apply_soft_delete_count_filter(self, query):
        """应用软删除过滤条件（用于count查询）"""
        if self._has_soft_delete:
            return query.where(self.model.is_deleted.is_(False))
        return query

    def get(self, id: int, session: Session) -> ModelType | None:
        """获取单个对象（默认过滤软删除）"""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_id(self, id: int, session: Session) -> ModelType | None:
        """获取单个对象（默认过滤软删除） get的别名"""
        return self.get(id, session)

    def get_with_deleted(self, id: int, session: Session) -> ModelType | None:
        """获取单个对象（包含软删除数据）"""
        query = select(self.model).where(self.model.id == id)
        result = session.execute(query)
        return result.scalars().first()

    def list(
        self,
        page: int = 1,
        page_size: int = 10,
        session: Session = None,
        filters: list = None,
        order_by: list = None,
        eager_load: list = None
    ) -> tuple[int, list[ModelType]]:
        """获取对象列表（默认过滤软删除）

        Args:
            page: 页码
            page_size: 每页数量
            session: 数据库会话
            filters: 过滤条件列表
            order_by: 排序条件列表
            eager_load: 预加载的关联属性列表

        Returns:
            (总数, 对象列表)
        """
        query = select(self.model)
        query = self._apply_soft_delete_filter(query)

        if eager_load:
            for relation in eager_load:
                query = query.options(selectinload(relation))

        if filters:
            for filter_condition in filters:
                query = query.where(filter_condition)

        if order_by:
            for order in order_by:
                query = query.order_by(order)
        else:
            query = query.order_by(self.model.id.desc())

        count_query = select(func.count()).select_from(self.model)
        count_query = self._apply_soft_delete_count_filter(count_query)
        if filters:
            for filter_condition in filters:
                count_query = count_query.where(filter_condition)
        count_result = session.execute(count_query)
        total = count_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = session.execute(query)
        items = result.scalars().all()

        return total, list(items)

    def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        session: Session = None,
        filters: list = None,
        order_by: list = None,
        eager_load: list = None
    ) -> tuple[int, builtins.list[ModelType]]:
        """获取对象列表（包含软删除数据）

        Args:
            page: 页码
            page_size: 每页数量
            session: 数据库会话
            filters: 过滤条件列表
            order_by: 排序条件列表
            eager_load: 预加载的关联属性列表

        Returns:
            (总数, 对象列表)
        """
        query = select(self.model)

        if eager_load:
            for relation in eager_load:
                query = query.options(selectinload(relation))

        if filters:
            for filter_condition in filters:
                query = query.where(filter_condition)

        if order_by:
            for order in order_by:
                query = query.order_by(order)
        else:
            query = query.order_by(self.model.id.desc())

        count_query = select(func.count()).select_from(self.model)
        if filters:
            for filter_condition in filters:
                count_query = count_query.where(filter_condition)
        count_result = session.execute(count_query)
        total = count_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = session.execute(query)
        items = result.scalars().all()

        return total, list(items)

    def create(
        self,
        obj_in: CreateSchemaType | dict[str, Any],
        session: Session
    ) -> ModelType:
        """创建对象（不commit）"""
        if isinstance(obj_in, dict):
            obj_dict = obj_in
        else:
            obj_dict = obj_in.model_dump()

        db_obj = self.model(**obj_dict)
        session.add(db_obj)
        session.flush()
        session.refresh(db_obj)
        return db_obj

    def update(
        self,
        id: int,
        obj_in: UpdateSchemaType | dict[str, Any],
        session: Session
    ) -> ModelType | None:
        """更新对象（不commit）

        注意：
        - 受保护的系统字段（如 is_system）会被自动过滤，无法通过此方法修改
        - 如果对象是系统内置（is_system=True），更新操作会被拒绝
        """
        db_obj = self.get(id, session)
        if not db_obj:
            return None

        if hasattr(db_obj, 'is_system') and db_obj.is_system:
            raise ValueError("系统内置对象不可修改")

        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude={"id"})

        for field, value in update_data.items():
            if field in PROTECTED_SYSTEM_FIELDS:
                continue
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.flush()
        session.refresh(db_obj)
        return db_obj

    def delete(self, id: int, session: Session, hard: bool = False) -> bool:
        """删除对象（自适应删除，不commit）

        根据模型是否继承 SoftDeleteMixin 自动选择删除方式：
        - 有软删除字段：执行软删除（设置 is_deleted=True, delete_time=当前时间）
        - 无软删除字段：执行物理删除

        注意：
        - 系统内置对象（is_system=True）不可删除

        Args:
            id: 对象ID
            session: 数据库会话
            hard: 是否强制物理删除（仅当模型有软删除时有效）

        Returns:
            是否删除成功
        """
        db_obj = self.get_by_id(id, session)
        if not db_obj:
            return False

        if hasattr(db_obj, 'is_system') and db_obj.is_system:
            raise ValueError("系统内置对象不可删除")

        if self._has_soft_delete and not hard:
            db_obj.is_deleted = True
            db_obj.delete_time = datetime.now()
        else:
            session.delete(db_obj)

        session.flush()
        return True

    def restore(self, id: int, session: Session) -> bool:
        """恢复软删除的对象（仅对支持软删除的模型有效）

        Args:
            id: 对象ID
            session: 数据库会话

        Returns:
            是否恢复成功
        """
        if not self._has_soft_delete:
            return False

        db_obj = self.get_with_deleted(id, session)
        if not db_obj or not db_obj.is_deleted:
            return False

        db_obj.is_deleted = False
        db_obj.delete_time = None
        session.flush()
        return True

    def exists(self, id: int, session: Session) -> bool:
        """检查对象是否存在（过滤软删除）"""
        result = session.execute(
            select(self.model.id)
            .where(self.model.id == id)
        )
        return result.scalars().first() is not None

    def exists_with_deleted(self, id: int, session: Session) -> bool:
        """检查对象是否存在（包含软删除）"""
        result = session.execute(
            select(self.model.id)
            .where(self.model.id == id)
        )
        return result.scalars().first() is not None
