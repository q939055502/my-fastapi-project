from fastapi.exceptions import HTTPException
from sqlalchemy import asc

from src.core.constants import (
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
)
from src.core.log import logger
from src.core.storage import UnitOfWork
from src.repositories.sys.tenant_plan_repository import tenant_plan_repository
from src.schemas.sys.tenant_plan import TenantPlanCreate, TenantPlanUpdate


class TenantPlanService:
    def __init__(self):
        self.repository = tenant_plan_repository
        self.logger = logger

    def get_plan_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
    ) -> tuple[int, list[dict]]:
        with UnitOfWork() as uow:
            search_filters = self._build_plan_search_filters(name=name)

            total, items = self.repository.list(
                page=page,
                page_size=page_size,
                session=uow.session,
                filters=search_filters,
                order_by=[asc(self.repository.model.sort), asc(self.repository.model.id)],
            )

            data = self._transform_plan_list(items)

            return total, data

    def get_plan_detail(self, plan_id: int) -> dict:
        with UnitOfWork() as uow:
            plan_obj = tenant_plan_repository.get(id=plan_id, session=uow.session)
            if not plan_obj:
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="套餐不存在")

            return self._transform_plan_detail(plan_obj)

    def create_plan(self, plan_in: TenantPlanCreate) -> dict:
        with UnitOfWork() as uow:
            existing_plan = tenant_plan_repository.is_exist(plan_in.code, session=uow.session)
            if existing_plan:
                raise HTTPException(
                    status_code=HTTP_BAD_REQUEST,
                    detail="The plan with this code already exists in the system.",
                )

            new_plan = tenant_plan_repository.create(obj_in=plan_in, session=uow.session)

            uow.commit()

            return self._transform_plan_detail(new_plan)

    def update_plan(self, plan_id: int, plan_in: TenantPlanUpdate) -> None:
        with UnitOfWork() as uow:
            existing_plan = tenant_plan_repository.get(id=plan_id, session=uow.session)
            if not existing_plan:
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="套餐不存在")

            if plan_in.code and plan_in.code != existing_plan.code:
                existing_by_code = tenant_plan_repository.is_exist(plan_in.code, session=uow.session)
                if existing_by_code:
                    raise HTTPException(
                        status_code=HTTP_BAD_REQUEST,
                        detail="The plan code already exists in the system.",
                    )

            tenant_plan_repository.update(id=plan_id, obj_in=plan_in, session=uow.session)
            uow.commit()

    def delete_plan(self, plan_id: int) -> None:
        with UnitOfWork() as uow:
            existing_plan = tenant_plan_repository.get(id=plan_id, session=uow.session)
            if not existing_plan:
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="套餐不存在")

            tenant_plan_repository.delete(id=plan_id, session=uow.session)

            uow.commit()

    def _build_plan_search_filters(self, name: str = "") -> list:
        filters = []

        if name:
            filters.append(self.repository.model.name.contains(name))

        return filters

    def _transform_plan_list(self, items) -> list[dict]:
        data = []

        for obj in items:
            plan_dict = self._transform_plan_detail(obj)
            data.append(plan_dict)

        return data

    def _transform_plan_detail(self, obj) -> dict:
        plan_dict = {}
        for column in obj.__table__.columns:
            field_name = column.name
            value = getattr(obj, field_name)
            plan_dict[field_name] = value

        return plan_dict


tenant_plan_service = TenantPlanService()
