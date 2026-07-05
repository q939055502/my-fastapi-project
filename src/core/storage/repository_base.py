"""Base Repository Class

通用 CRUD 仓库基类,仅包含与租户无关的通用能力:
- 软删除过滤与恢复
- 系统内置对象保护(is_system)

不包含租户隔离逻辑.租户隔离由各业务模块的二层基类负责(如 tenant/repository/base.py).
缓存清理由 service 层在写入后显式调用 cache_manager 完成.
"""
import builtins
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.core.base.protected_fields import CREATE_PROTECTED_FIELDS, UPDATE_PROTECTED_FIELDS
from src.core.exceptions import BusinessException
from src.core.storage.database import SessionLocal

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """通用 Repository 基类

    核心能力:
    - list(): 查询未删除的数据
    - list_deleted(): 查询已删除的数据(回收站)
    - 系统字段保护:is_system 对象不可修改/删除
    """

    def __init__(self, model: type[ModelType], resource_name: str | None = None):
        self.model = model
        self._has_soft_delete = self._check_soft_delete()
        self.resource_name = resource_name

    # ------------------------------------------------------------------
    # Session 辅助方法
    # ------------------------------------------------------------------
    def _get_session(self, session: Session | None = None) -> Session:
        """获取数据库会话

        如果传入 session,直接使用;否则创建新会话.
        注意:创建的新会话需要手动关闭.
        """
        if session is not None:
            return session
        return SessionLocal()

    # ------------------------------------------------------------------
    # 检测方法
    # ------------------------------------------------------------------
    def _check_soft_delete(self) -> bool:
        """检查模型是否支持软删除"""
        return hasattr(self.model, "delete_time")

    # ------------------------------------------------------------------
    # 过滤条件构建
    # ------------------------------------------------------------------
    def _apply_soft_delete_filter(self, query):
        """应用软删除过滤条件(仅查未删除)"""
        if self._has_soft_delete:
            return query.where(self.model.delete_time.is_(None))
        return query

    def _apply_soft_deleted_filter(self, query):
        """应用软删除过滤条件(仅查已删除)"""
        if self._has_soft_delete:
            return query.where(self.model.delete_time.isnot(None))
        return query

    def _apply_soft_delete_count_filter(self, query):
        """count 查询的软删除过滤(与 list 相同逻辑)"""
        if self._has_soft_delete:
            return query.where(self.model.delete_time.is_(None))
        return query

    def _apply_soft_deleted_count_filter(self, query):
        """count 查询的软删除过滤(与 list_deleted 相同逻辑)"""
        if self._has_soft_delete:
            return query.where(self.model.delete_time.isnot(None))
        return query

    # ------------------------------------------------------------------
    # 查询方法
    # ------------------------------------------------------------------
    def get(self, id: int, session: Session) -> ModelType | None:
        """按 ID 获取单个对象(过滤软删除)"""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_id(self, id: int, session: Session) -> ModelType | None:
        """get 的别名"""
        return self.get(id, session)

    def get_with_deleted(self, id: int, session: Session) -> ModelType | None:
        """按 ID 获取单个对象(包含软删除)"""
        query = select(self.model).where(self.model.id == id)
        result = session.execute(query)
        return result.scalars().first()

    def list(
        self,
        page: int = 1,
        page_size: int = 10,
        session: Session | None = None,
        filters: list | None = None,
        order_by: list | None = None,
        eager_load: list | None = None,
    ) -> tuple[int, list[ModelType]]:
        """列表查询(过滤软删除)

        Args:
            page: 页码,从 1 开始
            page_size: 每页数量
            session: 数据库会话
            filters: 过滤条件列表(SQLAlchemy where 子句)
            order_by: 排序条件列表
            eager_load: 预加载关联的属性列表(selectinload)

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

        # count 查询
        count_query = select(func.count()).select_from(self.model)
        count_query = self._apply_soft_delete_count_filter(count_query)
        if filters:
            for filter_condition in filters:
                count_query = count_query.where(filter_condition)
        count_result = session.execute(count_query)
        total = count_result.scalar()

        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = session.execute(query)
        items = result.scalars().all()

        return total, list(items)

    def list_deleted(
        self,
        page: int = 1,
        page_size: int = 10,
        session: Session | None = None,
        filters: builtins.list | None = None,
        order_by: builtins.list | None = None,
        eager_load: builtins.list | None = None,
    ) -> tuple[int, builtins.list[ModelType]]:
        """列表查询(仅查已删除的数据,回收站)

        Args:
            page: 页码,从 1 开始
            page_size: 每页数量
            session: 数据库会话
            filters: 过滤条件列表(SQLAlchemy where 子句)
            order_by: 排序条件列表
            eager_load: 预加载关联的属性列表(selectinload)

        Returns:
            (总数, 对象列表)
        """
        query = select(self.model)
        query = self._apply_soft_deleted_filter(query)

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

        # count 查询
        count_query = select(func.count()).select_from(self.model)
        count_query = self._apply_soft_deleted_count_filter(count_query)
        if filters:
            for filter_condition in filters:
                count_query = count_query.where(filter_condition)
        count_result = session.execute(count_query)
        total = count_result.scalar()

        # 分页
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = session.execute(query)
        items = result.scalars().all()

        return total, list(items)

    # ------------------------------------------------------------------
    # 写入方法
    # ------------------------------------------------------------------
    def create(
        self,
        obj_in: CreateSchemaType | dict[str, Any],
        session: Session,
    ) -> ModelType:
        """创建对象(不提交事务)

        自动过滤 CREATE_PROTECTED_FIELDS(安全敏感字段,前端不可传).
        如需自动填充租户ID, 创建人等,请使用二层基类.
        缓存清理由 service 层负责.
        """
        if isinstance(obj_in, dict):
            obj_dict = {k: v for k, v in obj_in.items() if k not in CREATE_PROTECTED_FIELDS}
        else:
            obj_dict = obj_in.model_dump(exclude=CREATE_PROTECTED_FIELDS)

        db_obj = self.model(**obj_dict)
        session.add(db_obj)
        session.flush()
        session.refresh(db_obj)

        return db_obj

    def update(
        self,
        id: int,
        obj_in: UpdateSchemaType | dict[str, Any],
        session: Session,
    ) -> ModelType | None:
        """更新对象(不提交事务)

        注意:系统内置对象(is_system=True)不可修改.
        受保护字段会被自动过滤.
        缓存清理由 service 层负责.
        """
        db_obj = self.get(id, session)
        if not db_obj:
            return None

        if getattr(db_obj, "is_system", False):
            raise BusinessException(40300, "系统内置对象不可修改")

        if isinstance(obj_in, dict):
            update_data = dict(obj_in)
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude={"id"})

        for field, value in update_data.items():
            if field in UPDATE_PROTECTED_FIELDS:
                continue
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.flush()
        session.refresh(db_obj)

        return db_obj

    def delete(self, id: int, session: Session, hard: bool = False) -> bool:
        """删除对象(自适应删除,不提交事务)

        有软删除字段 → 执行软删除(设置 delete_time)
        无软删除字段 → 执行物理删除

        系统内置对象(is_system=True)不可删除.
        缓存清理由 service 层负责.
        """
        db_obj = self.get_by_id(id, session)
        if not db_obj:
            return False

        if hasattr(db_obj, "is_system") and db_obj.is_system:
            raise BusinessException(40300, "系统内置对象不可删除")

        if self._has_soft_delete and not hard:
            db_obj.delete_time = datetime.now()
        else:
            session.delete(db_obj)

        session.flush()
        return True

    def restore(self, id: int, session: Session) -> bool:
        """恢复软删除的对象"""
        if not self._has_soft_delete:
            return False

        db_obj = self.get_with_deleted(id, session)
        if not db_obj or not db_obj.delete_time:
            return False

        db_obj.delete_time = None
        session.flush()
        return True

    # ------------------------------------------------------------------
    # 存在性检查
    # ------------------------------------------------------------------
    def exists(self, id: int, session: Session) -> bool:
        """检查对象是否存在(过滤软删除)"""
        query = select(self.model.id).where(self.model.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first() is not None

    def exists_with_deleted(self, id: int, session: Session) -> bool:
        """检查对象是否存在(包含软删除)"""
        query = select(self.model.id).where(self.model.id == id)
        result = session.execute(query)
        return result.scalars().first() is not None
