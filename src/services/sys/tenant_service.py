from sqlalchemy import asc

from src.core.enums.response_code import ResponseCode
from src.core.exceptions.exception import BusinessException
from src.core.storage import TransactionManager
from src.repositories.sys.tenant_repository import tenant_repository
from src.schemas.sys.tenant import TenantCreate, TenantUpdate


class TenantService:
    def __init__(self):
        self.repository = tenant_repository

    def get_tenant_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
        status: int = None,
    ) -> tuple[int, list[dict]]:
        with TransactionManager() as tm:
            search_filters = self._build_tenant_search_filters(
                name=name, status=status
            )

            total, items = self.repository.list(
                page=page,
                page_size=page_size,
                session=tm.session,
                filters=search_filters,
                order_by=[asc(self.repository.model.id)],
                eager_load=[self.repository.model.plan, self.repository.model.owner_user],
            )

            data = self._transform_tenant_list(items)

            return total, data

    def get_tenant_detail(self, tenant_id: int) -> dict:
        with TransactionManager() as tm:
            tenant_obj = tenant_repository.get(id=tenant_id, session=tm.session)
            if not tenant_obj:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="租户不存在")

            return self._transform_tenant_detail(tenant_obj)

    def create_tenant(self, tenant_in: TenantCreate) -> dict:
        with TransactionManager() as tm:
            existing_tenant = tenant_repository.is_exist(tenant_in.code, session=tm.session)
            if existing_tenant:
                raise BusinessException(
                    ResponseCode.PARAM_ERROR,
                    detail="The tenant with this code already exists in the system.",
                )

            new_tenant = tenant_repository.create(obj_in=tenant_in, session=tm.session)

            tm.commit()

            return self._transform_tenant_detail(new_tenant)

    def update_tenant(self, tenant_id: int, tenant_in: TenantUpdate) -> None:
        with TransactionManager() as tm:
            existing_tenant = tenant_repository.get(id=tenant_id, session=tm.session)
            if not existing_tenant:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="租户不存在")

            if tenant_in.code and tenant_in.code != existing_tenant.code:
                existing_by_code = tenant_repository.is_exist(tenant_in.code, session=tm.session)
                if existing_by_code:
                    raise BusinessException(
                        ResponseCode.PARAM_ERROR,
                        detail="The tenant code already exists in the system.",
                    )

            tenant_repository.update(id=tenant_id, obj_in=tenant_in, session=tm.session)
            tm.commit()

    def delete_tenant(self, tenant_id: int) -> None:
        with TransactionManager() as tm:
            existing_tenant = tenant_repository.get(id=tenant_id, session=tm.session)
            if not existing_tenant:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="租户不存在")

            tenant_repository.delete(id=tenant_id, session=tm.session)

            tm.commit()

    def _build_tenant_search_filters(
        self,
        name: str = "",
        status: int = None,
    ) -> list:
        filters = []

        if name:
            filters.append(self.repository.model.name.contains(name))

        if status is not None:
            filters.append(self.repository.model.status == str(status))

        return filters

    def _transform_tenant_list(self, items) -> list[dict]:
        data = []

        for obj in items:
            tenant_dict = self._transform_tenant_detail(obj)
            data.append(tenant_dict)

        return data

    def _transform_tenant_detail(self, obj) -> dict:
        tenant_dict = {}
        for column in obj.__table__.columns:
            field_name = column.name
            value = getattr(obj, field_name)
            tenant_dict[field_name] = value

        if hasattr(obj, "plan") and obj.plan:
            tenant_dict["plan"] = {
                "id": obj.plan.id,
                "name": obj.plan.name,
                "code": obj.plan.code,
            }
        else:
            tenant_dict["plan"] = None

        if hasattr(obj, "owner_user") and obj.owner_user:
            tenant_dict["owner_user"] = {
                "id": obj.owner_user.id,
                "username": obj.owner_user.username,
            }
        else:
            tenant_dict["owner_user"] = None

        return tenant_dict


tenant_service = TenantService()
