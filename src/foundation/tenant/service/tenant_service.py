from sqlalchemy import asc, select
from src.core.base.service_base import BaseService
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.system.repository.user_repository import user_repository
from src.foundation.tenant.repository.quota_repository import quota_repository
from src.foundation.tenant.repository.tenant_repository import tenant_repository
from src.foundation.tenant.schemas.tenant import (
    TenantCreate,
    TenantOwnerUser,
    TenantQuota,
    TenantUpdate,
)
from src.models.platform.auth.account_bind import AccountBind
from src.models.tenant import Tenant


class TenantService(BaseService):
    def __init__(self):
        super().__init__()
        self.repository = tenant_repository

    def get_tenant_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
        status: bool = None,
    ) -> tuple[int, list[Tenant]]:
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

            return total, items

    def get_tenant_detail(self, tenant_uuid: str) -> Tenant:
        with TransactionManager() as tm:
            tenant_id = self.get_id_by_uuid("tenant", tenant_uuid, tm.session)
            if not tenant_id:
                raise BusinessException(40401, detail="租户不存在")

            tenant_obj = tenant_repository.get(id=tenant_id, session=tm.session)
            if not tenant_obj:
                raise BusinessException(40401, detail="租户不存在")

            return tenant_obj

    def create_tenant(self, tenant_in: TenantCreate) -> Tenant:
        with TransactionManager() as tm:
            existing_tenant = tenant_repository.is_exist(tenant_in.code, session=tm.session)
            if existing_tenant:
                raise BusinessException(
                    40000,
                    detail="The tenant with this code already exists in the system.",
                )

            if tenant_in.owner_user_uuid:
                owner_user_id = self.get_id_by_uuid("user", str(tenant_in.owner_user_uuid), tm.session)
                if not owner_user_id:
                    raise BusinessException(40401, detail="户主用户不存在")
                owner_user = user_repository.get(id=owner_user_id, session=tm.session)
            else:
                owner_user = None

            tenant_data = tenant_in.model_dump(exclude={"owner_user_uuid"})
            if owner_user:
                tenant_data["owner_user_id"] = owner_user.id

            new_tenant = tenant_repository.create(obj_in=tenant_data, session=tm.session)

            tm.commit()

            return new_tenant

    def update_tenant(self, tenant_uuid: str, tenant_in: TenantUpdate) -> None:
        with TransactionManager() as tm:
            tenant_id = self.get_id_by_uuid("tenant", tenant_uuid, tm.session)
            if not tenant_id:
                raise BusinessException(40401, detail="租户不存在")

            existing_tenant = tenant_repository.get(id=tenant_id, session=tm.session)
            if not existing_tenant:
                raise BusinessException(40401, detail="租户不存在")

            if tenant_in.code and tenant_in.code != existing_tenant.code:
                existing_by_code = tenant_repository.is_exist(tenant_in.code, session=tm.session)
                if existing_by_code:
                    raise BusinessException(
                        40000,
                        detail="The tenant code already exists in the system.",
                    )

            tenant_repository.update(id=existing_tenant.id, obj_in=tenant_in, session=tm.session)
            tm.commit()

    def delete_tenant(self, tenant_uuid: str) -> None:
        with TransactionManager() as tm:
            tenant_id = self.get_id_by_uuid("tenant", tenant_uuid, tm.session)
            if not tenant_id:
                raise BusinessException(40401, detail="租户不存在")

            existing_tenant = tenant_repository.get(id=tenant_id, session=tm.session)
            if not existing_tenant:
                raise BusinessException(40401, detail="租户不存在")

            tenant_repository.delete(id=existing_tenant.id, session=tm.session)

            tm.commit()

    def get_tenant_owner_user(self, tenant: Tenant, session) -> TenantOwnerUser | None:
        """获取租户户主用户信息"""
        if not tenant.owner_user_id:
            return None

        owner_user = user_repository.get(id=tenant.owner_user_id, session=session)
        if not owner_user:
            return None

        # 查询邮箱
        email_query = select(AccountBind).where(
            AccountBind.user_id == owner_user.id,
            AccountBind.bind_type == 1,
            AccountBind.status == "verified",
            AccountBind.delete_time.is_(None)
        )
        email_result = session.execute(email_query).scalars().first()
        email = email_result.identifier if email_result else None

        return TenantOwnerUser(
            uuid=owner_user.uuid,
            username=owner_user.username,
            email=email
        )

    def get_tenant_quota(self, tenant: Tenant, session) -> TenantQuota | None:
        """获取租户配额信息"""
        if not tenant.owner_user_id:
            return None

        quota = quota_repository.get_by_tenant_id(tenant.id, session)
        if not quota:
            return None

        return TenantQuota(
            id=quota.id,
            name=quota.name if hasattr(quota, 'name') else None,
            code=quota.code if hasattr(quota, 'code') else None
        )

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


tenant_service = TenantService()
