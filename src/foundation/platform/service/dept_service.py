from uuid import UUID

from sqlalchemy import asc
from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.storage import TransactionManager
from src.foundation.platform.repository.dept_repository import dept_repository
from src.foundation.platform.schemas.dept import DeptCreate, DeptUpdate


class DeptService:
    def __init__(self):
        self.repository = dept_repository

    def get_dept_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
    ) -> tuple[int, list[dict]]:
        with TransactionManager() as tm:
            search_filters = self._build_dept_search_filters(
                name=name
            )

            total, items = self.repository.list(
                page=page,
                page_size=page_size,
                session=tm.session,
                filters=search_filters,
                order_by=[asc(self.repository.model.sort)],
            )

            data = self._transform_dept_list(items)

            return total, data

    def get_dept_detail(self, dept_uuid: UUID) -> dict:
        with TransactionManager() as tm:
            dept_obj = dept_repository.get_by_uuid(uuid=dept_uuid, session=tm.session)
            if not dept_obj:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="部门不存在")

            dept_dict = {}
            for column in dept_obj.__table__.columns:
                field_name = column.name
                value = getattr(dept_obj, field_name)
                dept_dict[field_name] = value

            return dept_dict

    def get_dept_tree(self, name: str = "") -> list[dict]:
        with TransactionManager() as tm:
            return dept_repository.get_dept_tree(name=name, session=tm.session)

    def create_dept(self, dept_in: DeptCreate) -> None:
        with TransactionManager() as tm:
            if dept_in.parent_uuid:
                parent_dept = dept_repository.get_by_uuid(uuid=dept_in.parent_uuid, session=tm.session)
                if not parent_dept:
                    raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="父部门不存在")

            dept_repository.create_dept(obj_in=dept_in, session=tm.session)

            tm.commit()

    def update_dept(self, dept_uuid: UUID, dept_in: DeptUpdate) -> None:
        with TransactionManager() as tm:
            existing_dept = dept_repository.get_by_uuid(uuid=dept_uuid, session=tm.session)
            if not existing_dept:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="部门不存在")

            if dept_in.parent_uuid:
                parent_dept = dept_repository.get_by_uuid(uuid=dept_in.parent_uuid, session=tm.session)
                if not parent_dept:
                    raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="父部门不存在")

            if dept_in.parent_uuid == dept_uuid:
                raise BusinessException(ResponseCode.PARAM_ERROR, detail="父部门不能是自身")

            dept_repository.update_dept(dept_uuid=dept_uuid, obj_in=dept_in, session=tm.session)

            tm.commit()

    def delete_dept(self, dept_uuid: UUID) -> None:
        with TransactionManager() as tm:
            existing_dept = dept_repository.get_by_uuid(uuid=dept_uuid, session=tm.session)
            if not existing_dept:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="部门不存在")

            dept_repository.delete_dept(dept_uuid=dept_uuid, session=tm.session)

            tm.commit()

    def _build_dept_search_filters(
        self,
        name: str = "",
    ) -> list:
        filters = []

        if name:
            filters.append(self.repository.model.name.contains(name))

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