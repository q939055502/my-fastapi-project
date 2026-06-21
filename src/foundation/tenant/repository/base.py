"""Tenant Repository Base

租户侧 Repository 基类,在通用 Repository 基础上增加租户隔离能力。

核心职责:
1. 所有查询自动加上 tenant_id 过滤(依据当前请求上下文)
2. 创建对象时自动填充 tenant_id
3. 路径租户(path_tenant_id)优先于认证租户(tenant_id)

适用场景:
- 租户内的业务数据模型(有 tenant_id 字段)
- 平台管理员操作租户数据时(通过路径租户定位)

不适用场景:
- Tenant 模型本身(自己管理自己)
- 平台级数据(没有 tenant_id 字段)
"""
import builtins
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from src.core.exceptions import BusinessException
from src.core.storage import BaseRepository
from src.foundation.iam.auth.context import get_current_auth_context

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class TenantRepositoryBase(BaseRepository[ModelType, CreateSchemaType, UpdateSchemaType]):
    """租户 Repository 基类

    在 BaseRepository 基础上,增加了:
    - 从请求上下文自动获取租户 ID
    - 所有查询自动按 tenant_id 过滤
    - 创建对象时自动填充 tenant_id
    """

    def __init__(self, model: type[ModelType], resource_name: str | None = None):
        super().__init__(model=model, resource_name=resource_name)
        # 确保模型有 tenant_id 字段
        if not hasattr(self.model, "tenant_id"):
            raise TypeError(
                f"Model {self.model.__name__} has no 'tenant_id' column. "
                "Use BaseRepository instead of TenantRepositoryBase."
            )

    # ------------------------------------------------------------------
    # 上下文辅助
    # ------------------------------------------------------------------
    def _get_tenant_id(self) -> int | None:
        """获取当前上下文的生效租户 ID（path_tenant_id 优先于 tenant_id）"""
        ctx = get_current_auth_context()
        if ctx is None:
            return None
        return ctx.path_tenant_id or ctx.tenant_id

    def _ensure_tenant_id(self) -> int:
        """获取租户 ID,不存在时抛异常(用于必须有租户的场景)"""
        tenant_id = self._get_tenant_id()
        if not tenant_id:
            raise BusinessException(40000, "未找到租户上下文")
        return tenant_id

    # ------------------------------------------------------------------
    # 过滤条件构建(在父类软删除过滤基础上,叠加租户过滤)
    # ------------------------------------------------------------------
    def _apply_tenant_filter(self, query):
        """给查询添加 tenant_id 过滤"""
        tenant_id = self._get_tenant_id()
        if tenant_id is None:
            return query
        return query.where(self.model.tenant_id == tenant_id)

    def _apply_all_default_filters(self, query):
        """应用所有默认过滤(软删除 + 租户)"""
        query = self._apply_soft_delete_filter(query)
        query = self._apply_tenant_filter(query)
        return query

    # ------------------------------------------------------------------
    # 查询方法(全部叠加租户过滤)
    # ------------------------------------------------------------------
    def get(self, id: int, session: Session) -> ModelType | None:
        """按 ID 获取单个对象(过滤软删除 + 租户)"""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_all_default_filters(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_id(self, id: int, session: Session) -> ModelType | None:
        """get 的别名"""
        return self.get(id, session)

    def get_with_deleted(self, id: int, session: Session) -> ModelType | None:
        """按 ID 获取单个对象(包含软删除,仍按租户过滤)"""
        query = select(self.model).where(self.model.id == id)
        query = self._apply_tenant_filter(query)
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
        """租户内列表查询(过滤软删除 + 租户)"""
        query = select(self.model)
        query = self._apply_all_default_filters(query)

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
        count_query = self._apply_soft_delete_filter(count_query)
        count_query = self._apply_tenant_filter(count_query)
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
        filters: builtins.list | None = None,
        order_by: builtins.list | None = None,
        eager_load: builtins.list | None = None,
    ) -> tuple[int, builtins.list[ModelType]]:
        """租户内列表查询(包含软删除,仍按租户过滤)"""
        query = select(self.model)
        query = self._apply_tenant_filter(query)

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
        count_query = self._apply_tenant_filter(count_query)
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
    # 写入方法(创建时自动填充 tenant_id)
    # ------------------------------------------------------------------
    def create(
        self,
        obj_in: CreateSchemaType | dict[str, Any],
        session: Session,
    ) -> ModelType:
        """创建对象(自动填充 tenant_id,不提交事务)"""
        if isinstance(obj_in, dict):
            obj_dict = dict(obj_in)
        else:
            obj_dict = obj_in.model_dump()

        # 自动填充 tenant_id
        if obj_dict.get("tenant_id") is None:
            tenant_id = self._get_tenant_id()
            if tenant_id:
                obj_dict["tenant_id"] = tenant_id

        db_obj = self.model(**obj_dict)
        session.add(db_obj)
        session.flush()
        session.refresh(db_obj)

        self._clear_resource_cache()
        return db_obj

    def exists(self, id: int, session: Session) -> bool:
        """检查对象是否存在(过滤软删除 + 租户)"""
        query = select(self.model.id).where(self.model.id == id)
        query = self._apply_all_default_filters(query)
        result = session.execute(query)
        return result.scalars().first() is not None

    def exists_with_deleted(self, id: int, session: Session) -> bool:
        """检查对象是否存在(包含软删除,仍按租户过滤)"""
        query = select(self.model.id).where(self.model.id == id)
        query = self._apply_tenant_filter(query)
        result = session.execute(query)
        return result.scalars().first() is not None
