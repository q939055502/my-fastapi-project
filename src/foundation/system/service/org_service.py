from uuid import UUID

from sqlalchemy import asc
from src.core.enums.response_code import ResponseCode
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.system.repository.org_repository import org_repository
from src.foundation.system.schemas.org import OrgCreate, OrgUpdate


class OrgService:
    def __init__(self):
        self.repository = org_repository

    def get_org_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
    ) -> tuple[int, list[dict]]:
        with TransactionManager() as tm:
            search_filters = self._build_org_search_filters(
                name=name
            )

            total, items = self.repository.list(
                page=page,
                page_size=page_size,
                session=tm.session,
                filters=search_filters,
                order_by=[asc(self.repository.model.sort)],
            )

            data = self._transform_org_list(items)

            return total, data

    def get_org_detail(self, org_uuid: UUID) -> dict:
        with TransactionManager() as tm:
            org_obj = org_repository.get_by_uuid(uuid=org_uuid, session=tm.session)
            if not org_obj:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="组织不存在")

            org_dict = {}
            for column in org_obj.__table__.columns:
                field_name = column.name
                if field_name != "id":
                    value = getattr(org_obj, field_name)
                    org_dict[field_name] = value

            return org_dict

    def get_org_tree(self, name: str = "") -> list[dict]:
        with TransactionManager() as tm:
            return org_repository.get_org_tree(name=name, session=tm.session)

    def create_org(self, org_in: OrgCreate) -> None:
        with TransactionManager() as tm:
            if org_in.parent_uuid:
                parent_org = org_repository.get_by_uuid(uuid=org_in.parent_uuid, session=tm.session)
                if not parent_org:
                    raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="父组织不存在")

            org_repository.create_org(obj_in=org_in, session=tm.session)

            tm.commit()

    def update_org(self, org_uuid: UUID, org_in: OrgUpdate) -> None:
        with TransactionManager() as tm:
            existing_org = org_repository.get_by_uuid(uuid=org_uuid, session=tm.session)
            if not existing_org:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="组织不存在")

            if org_in.parent_uuid:
                parent_org = org_repository.get_by_uuid(uuid=org_in.parent_uuid, session=tm.session)
                if not parent_org:
                    raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="父组织不存在")

            if org_in.parent_uuid == org_uuid:
                raise BusinessException(ResponseCode.PARAM_ERROR, detail="父组织不能是自身")

            org_repository.update_org(org_uuid=org_uuid, obj_in=org_in, session=tm.session)

            tm.commit()

    def delete_org(self, org_uuid: UUID) -> None:
        with TransactionManager() as tm:
            existing_org = org_repository.get_by_uuid(uuid=org_uuid, session=tm.session)
            if not existing_org:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="组织不存在")

            org_repository.delete_org(org_uuid=org_uuid, session=tm.session)

            tm.commit()

    def _build_org_search_filters(
        self,
        name: str = "",
    ) -> list:
        filters = []

        if name:
            filters.append(self.repository.model.name.contains(name))

        return filters

    def _transform_org_list(self, items) -> list[dict]:
        data = []

        for obj in items:
            org_dict = {}
            for column in obj.__table__.columns:
                field_name = column.name
                if field_name != "id":
                    value = getattr(obj, field_name)
                    org_dict[field_name] = value

            data.append(org_dict)

        return data


org_service = OrgService()