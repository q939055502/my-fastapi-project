from fastapi.exceptions import HTTPException

from src.repositories.sys.dept_repository import dept_repository
from src.schemas.sys.depts import DeptCreate, DeptUpdate
from src.core.log import logger
from src.core.storage import UnitOfWork
from sqlalchemy import asc


class DeptService:
    def __init__(self):
        self.repository = dept_repository
        self.logger = logger

    def get_dept_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
    ) -> tuple[int, list[dict]]:
        with UnitOfWork() as uow:
            search_filters = self._build_dept_search_filters(
                name=name
            )

            total, items = self.repository.list(
                page=page,
                page_size=page_size,
                session=uow.session,
                filters=search_filters,
                order_by=[asc(self.repository.model.sort)],
            )

            data = self._transform_dept_list(items)

            return total, data

    def get_dept_detail(self, dept_id: int) -> dict:
        with UnitOfWork() as uow:
            dept_obj = dept_repository.get(id=dept_id, session=uow.session)
            if not dept_obj:
                raise HTTPException(status_code=404, detail="部门不存在")

            dept_dict = {}
            for column in dept_obj.__table__.columns:
                field_name = column.name
                value = getattr(dept_obj, field_name)
                dept_dict[field_name] = value

            return dept_dict

    def get_dept_tree(self, name: str = "") -> list[dict]:
        with UnitOfWork() as uow:
            return dept_repository.get_dept_tree(name=name, session=uow.session)

    def create_dept(self, dept_in: DeptCreate) -> None:
        with UnitOfWork() as uow:
            if dept_in.parent_id != 0:
                parent_dept = dept_repository.get(id=dept_in.parent_id, session=uow.session)
                if not parent_dept:
                    raise HTTPException(status_code=404, detail="父部门不存在")

            dept_repository.create_dept(obj_in=dept_in, session=uow.session)

            uow.commit()

    def update_dept(self, dept_id: int, dept_in: DeptUpdate) -> None:
        with UnitOfWork() as uow:
            existing_dept = dept_repository.get(id=dept_id, session=uow.session)
            if not existing_dept:
                raise HTTPException(status_code=404, detail="部门不存在")

            if dept_in.parent_id != 0:
                parent_dept = dept_repository.get(id=dept_in.parent_id, session=uow.session)
                if not parent_dept:
                    raise HTTPException(status_code=404, detail="父部门不存在")

            if dept_in.parent_id == dept_id:
                raise HTTPException(status_code=400, detail="父部门不能是自身")

            dept_repository.update_dept(dept_id=dept_id, obj_in=dept_in, session=uow.session)

            uow.commit()

    def delete_dept(self, dept_id: int) -> None:
        with UnitOfWork() as uow:
            existing_dept = dept_repository.get(id=dept_id, session=uow.session)
            if not existing_dept:
                raise HTTPException(status_code=404, detail="部门不存在")

            dept_repository.delete_dept(dept_id=dept_id, session=uow.session)

            uow.commit()

    def _build_dept_search_filters(
        self,
        name: str = "",
    ) -> list:
        filters = []

        if name:
            filters.append(self.repository.model.name.contains(name))

        filters.append(self.repository.model.is_deleted == False)

        return filters

    def _transform_dept_list(self, items) -> list[dict]:
        data = []

        for obj in items:
            dept_dict = {}
            for column in obj.__table__.columns:
                field_name = column.name
                value = getattr(obj, field_name)
                dept_dict[field_name] = value

            data.append(dept_dict)

        return data


dept_service = DeptService()
