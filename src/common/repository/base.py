"""Generic Repository Base Class

通用 CRUD 仓库基类，仅包含与租户无关的通用能力：
- 软删除过滤与恢复
- 系统内置对象保护（is_system）
- 写入操作自动清理缓存

不包含租户隔离逻辑。租户隔离由各业务模块的二层基类负责（如 tenant/repository/base.py）。
"""
from datetime import datetime
from typing import Any, Generic, List, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


# 受保护字段：更新/创建时不可修改
PROTECTED_SYSTEM_FIELDS = {
    "id",
    "delete_time",
    "is_system",
    "created_at",
    "updated_at",
    "create_user_id",
    "update_user_id",
    "tenant_id",
}


class GenericRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """通用 Repository 基类

    核心能力：
    - 双态查询：list() 过滤软删除，list_all() 包含软删除
    - 系统字段保护：is_system 对象不可修改/删除
    - 写入缓存清理：创建/更新/删除后调用缓存管理器清理该资源缓存
    """

    def __init__(self, model: type[ModelType], resource_name: str | None = None):
        self.model = model
        self._has_soft_delete = self._check_soft_delete()
        self.resource_name = resource_name

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
        """应用软删除过滤条件（仅查未删除）"""
        if self._has_soft_delete:
            return query.where(self.model.delete_time.is_(None))
        return query

    def _apply_soft_delete_count_filter(self, query):
        """count 查询的软删除过滤（与 list 相同逻辑）"""
        if self._has_soft_delete:
            return query.where(self.model.delete_time.is_(None))
        return query

    # ------------------------------------------------------------------
    # 缓存清理
    # ------------------------------------------------------------------
    def _clear_resource_cache(self):
        """写入操作后清理该资源的所有缓存"""
        if not self.resource_name:
            return
        try:
            from src.common.core.storage.cache import cache_manager

            cache_manager.delete_by_resource(self.resource_name, include_scope=True)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # 查询方法
    # ------------------------------------------------------------------
    def get(self, id: int, session: Session) -> ModelType | None:
        """按 ID 获取单个对象（过滤软删除）"""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_id(self, id: int, session: Session) -> ModelType | None:
        """get 的别名"""
        return self.get(id, session)

    def get_by_uuid(self, uuid: UUID, session: Session) -> ModelType | None:
        """按 UUID 获取单个对象（过滤软删除）"""
        if not hasattr(self.model, "uuid"):
            return None
        query = select(self.model).where(self.model.uuid == uuid)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_with_deleted(self, id: int, session: Session) -> ModelType | None:
        """按 ID 获取单个对象（包含软删除）"""
        query = select(self.model).where(self.model.id == id)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_uuid_with_deleted(self, uuid: UUID, session: Session) -> ModelType | None:
        """按 UUID 获取单个对象（包含软删除）"""
        if not hasattr(self.model, "uuid"):
            return None
        query = select(self.model).where(self.model.uuid == uuid)
        result = session.execute(query)
        return result.scalars().first()

    def list(
        self,
        page: int = 1,
        page_size: int = 10,
        session: Session | None = None,
        filters: List | None = None,
        order_by: List | None = None,
        eager_load: List | None = None,
    ) -> tuple[int, List[ModelType]]:
        """列表查询（过滤软删除）

        Args:
            page: 页码，从 1 开始
            page_size: 每页数量
            session: 数据库会话
            filters: 过滤条件列表（SQLAlchemy where 子句）
            order_by: 排序条件列表
            eager_load: 预加载关联的属性列表（selectinload）

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

    def list_all(
        self,
        page: int = 1,
        page_size: int = 10,
        session: Session | None = None,
        filters: List | None = None,
        order_by: List | None = None,
        eager_load: List | None = None,
    ) -> tuple[int, List[ModelType]]:
        """列表查询（包含软删除）"""
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

        # count 查询
        count_query = select(func.count()).select_from(self.model)
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
        """创建对象（不提交事务）

        注意：此方法仅做通用对象创建，不自动填充任何字段。
        如需自动填充租户ID、创建人等，请使用二层基类。
        """
        if isinstance(obj_in, dict):
            obj_dict = dict(obj_in)
        else:
            obj_dict = obj_in.model_dump()

        db_obj = self.model(**obj_dict)
        session.add(db_obj)
        session.flush()
        session.refresh(db_obj)

        self._clear_resource_cache()
        return db_obj

    def update(
        self,
        id: int,
        obj_in: UpdateSchemaType | dict[str, Any],
        session: Session,
    ) -> ModelType | None:
        """更新对象（不提交事务）

        注意：系统内置对象（is_system=True）不可修改。
        受保护字段（id/delete_time/is_system/tenant_id 等）会被自动过滤。
        """
        db_obj = self.get(id, session)
        if not db_obj:
            return None

        if getattr(db_obj, "is_system", False):
            raise BusinessException(ResponseCode.FORBIDDEN, "系统内置对象不可修改")

        if isinstance(obj_in, dict):
            update_data = dict(obj_in)
        else:
            update_data = obj_in.model_dump(exclude_unset=True, exclude={"id"})

        for field, value in update_data.items():
            if field in PROTECTED_SYSTEM_FIELDS:
                continue
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.flush()
        session.refresh(db_obj)

        self._clear_resource_cache()
        return db_obj

    def delete(self, id: int, session: Session, hard: bool = False) -> bool:
        """删除对象（自适应删除，不提交事务）

        有软删除字段 → 执行软删除（设置 delete_time）
        无软删除字段 → 执行物理删除

        系统内置对象（is_system=True）不可删除。
        """
        db_obj = self.get_by_id(id, session)
        if not db_obj:
            return False

        if hasattr(db_obj, "is_system") and db_obj.is_system:
            raise BusinessException(ResponseCode.FORBIDDEN, "系统内置对象不可删除")

        if self._has_soft_delete and not hard:
            db_obj.delete_time = datetime.now()
        else:
            session.delete(db_obj)

        session.flush()

        self._clear_resource_cache()
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
        """检查对象是否存在（过滤软删除）"""
        query = select(self.model.id).where(self.model.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first() is not None

    def exists_with_deleted(self, id: int, session: Session) -> bool:
        """检查对象是否存在（包含软删除）"""
        query = select(self.model.id).where(self.model.id == id)
        result = session.execute(query)
        return result.scalars().first() is not None
