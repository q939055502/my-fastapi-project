from sqlalchemy import asc

from src.core.base.service_base import BaseService
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.system.repository.org_repository import org_repository
from src.foundation.system.schemas.org import OrgCreate, OrgUpdate
from src.models.platform import Org


class OrgService(BaseService):
    def __init__(self):
        super().__init__()
        self.repository = org_repository

    def get_org_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
    ) -> tuple[int, list[Org]]:
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

            return total, items

    def get_org_detail(self, org_uuid: str) -> Org:
        with TransactionManager() as tm:
            org_id = self.get_id_by_uuid("org", org_uuid, tm.session)
            if not org_id:
                raise BusinessException(40401, detail="组织不存在")

            org_obj = org_repository.get(id=org_id, session=tm.session)
            if not org_obj:
                raise BusinessException(40401, detail="组织不存在")

            return org_obj

    def get_org_tree(self, name: str = "") -> list[Org]:
        with TransactionManager() as tm:
            return org_repository.get_org_tree(name=name, session=tm.session)

    def create_org(self, org_in: OrgCreate) -> Org:
        with TransactionManager() as tm:
            if org_in.parent_uuid:
                parent_id = self.get_id_by_uuid("org", str(org_in.parent_uuid), tm.session)
                if not parent_id:
                    raise BusinessException(40401, detail="父组织不存在")

            org = org_repository.create_org(obj_in=org_in, session=tm.session)
            tm.commit()
            return org

    def update_org(self, org_uuid: str, org_in: OrgUpdate) -> None:
        with TransactionManager() as tm:
            org_id = self.get_id_by_uuid("org", org_uuid, tm.session)
            if not org_id:
                raise BusinessException(40401, detail="组织不存在")

            existing_org = org_repository.get(id=org_id, session=tm.session)
            if not existing_org:
                raise BusinessException(40401, detail="组织不存在")

            if org_in.parent_uuid:
                parent_id = self.get_id_by_uuid("org", str(org_in.parent_uuid), tm.session)
                if not parent_id:
                    raise BusinessException(40401, detail="父组织不存在")

            if org_in.parent_uuid and str(org_in.parent_uuid) == org_uuid:
                raise BusinessException(40000, detail="父组织不能是自身")

            org_repository.update_org(org_id=org_id, obj_in=org_in, session=tm.session)

            tm.commit()

    def delete_org(self, org_uuid: str) -> None:
        with TransactionManager() as tm:
            org_id = self.get_id_by_uuid("org", org_uuid, tm.session)
            if not org_id:
                raise BusinessException(40401, detail="组织不存在")

            existing_org = org_repository.get(id=org_id, session=tm.session)
            if not existing_org:
                raise BusinessException(40401, detail="组织不存在")

            org_repository.delete_org(org_id=org_id, session=tm.session)

            tm.commit()

    def _build_org_search_filters(
        self,
        name: str = "",
    ) -> list:
        filters = []

        if name:
            filters.append(self.repository.model.name.contains(name))

        return filters


org_service = OrgService()
