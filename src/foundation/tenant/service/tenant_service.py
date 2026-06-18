from uuid import UUID

from sqlalchemy import asc, select
from src.core.enums.response_code import ResponseCode
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.system.repository.user_repository import user_repository
from src.foundation.tenant.repository.tenant_repository import tenant_repository
from src.foundation.tenant.repository.quota_repository import quota_repository
from src.models.platform import AccountBind
from src.foundation.tenant.schemas.tenant import TenantCreate, TenantUpdate


class TenantService:
    def __init__(self):
        self.repository = tenant_repository

    def get_tenant_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
        status: bool = None,
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
            )

            data = self._transform_tenant_list(items, tm.session)

            return total, data

    def get_tenant_detail(self, tenant_uuid: UUID) -> dict:
        with TransactionManager() as tm:
            tenant_obj = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=tm.session)

            if not tenant_obj:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="租户不存在")

            return self._transform_tenant_detail(tenant_obj, tm.session)

    def create_tenant(self, tenant_in: TenantCreate) -> dict:
        with TransactionManager() as tm:
            existing_tenant = tenant_repository.is_exist(tenant_in.code, session=tm.session)
            if existing_tenant:
                raise BusinessException(
                    ResponseCode.PARAM_ERROR,
                    detail="The tenant with this code already exists in the system.",
                )

            owner_user = user_repository.get_by_uuid(uuid=tenant_in.owner_user_uuid, session=tm.session)
            if not owner_user:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="户主用户不存在")

            tenant_data = tenant_in.model_dump(exclude={"owner_user_uuid"})
            tenant_data["owner_user_id"] = owner_user.id

            new_tenant = tenant_repository.create(obj_in=tenant_data, session=tm.session)

            tm.commit()

            return self._transform_tenant_detail(new_tenant, tm.session)

    def update_tenant(self, tenant_uuid: UUID, tenant_in: TenantUpdate) -> None:
        with TransactionManager() as tm:
            existing_tenant = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=tm.session)
            if not existing_tenant:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="租户不存在")

            if tenant_in.code and tenant_in.code != existing_tenant.code:
                existing_by_code = tenant_repository.is_exist(tenant_in.code, session=tm.session)
                if existing_by_code:
                    raise BusinessException(
                        ResponseCode.PARAM_ERROR,
                        detail="The tenant code already exists in the system.",
                    )

            tenant_repository.update(id=existing_tenant.id, obj_in=tenant_in, session=tm.session)
            tm.commit()

    def delete_tenant(self, tenant_uuid: UUID) -> None:
        with TransactionManager() as tm:
            existing_tenant = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=tm.session)
            if not existing_tenant:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="租户不存在")

            tenant_repository.delete(id=existing_tenant.id, session=tm.session)

            tm.commit()

    def _build_tenant_search_filters(
        self,
        name: str = "",
        status: bool = None,
    ) -> list:
        filters = []

        if name:
            filters.append(self.repository.model.name.contains(name))

        if status is not None:
            filters.append(self.repository.model.status == status)

        return filters

    def _transform_tenant_list(self, items, session) -> list[dict]:
        data = []

        for obj in items:
            tenant_dict = self._transform_tenant_detail(obj, session)
            data.append(tenant_dict)

        return data

    def _transform_tenant_detail(self, obj, session) -> dict:
        tenant_dict = {}
        for column in obj.__table__.columns:
            field_name = column.name
            value = getattr(obj, field_name)
            tenant_dict[field_name] = value

        # 查询 quota 信息
        if obj.owner_user_id:
            quota = quota_repository.get_by_tenant_id(obj.id, session)
            if quota:
                tenant_dict["quota"] = {
                    "id": quota.id,
                    "name": quota.name if hasattr(quota, 'name') else None,
                    "code": quota.code if hasattr(quota, 'code') else None,
                }
            else:
                tenant_dict["quota"] = None
        else:
            tenant_dict["quota"] = None

        # 查询 owner_user 信息
        if obj.owner_user_id:
            owner_user = user_repository.get(id=obj.owner_user_id, session=session)
            if owner_user:
                # 查询 owner_user 的邮箱绑定
                email_query = select(AccountBind).where(
                    AccountBind.user_id == owner_user.id,
                    AccountBind.bind_type == 1,
                    AccountBind.status == "verified",
                    AccountBind.delete_time.is_(None)
                )
                email_result = session.execute(email_query).scalars().first()
                email = email_result.identifier if email_result else None

                tenant_dict["owner_user"] = {
                    "uuid": owner_user.uuid,
                    "username": owner_user.username,
                    "email": email,
                }
            else:
                tenant_dict["owner_user"] = None
        else:
            tenant_dict["owner_user"] = None

        return tenant_dict


tenant_service = TenantService()