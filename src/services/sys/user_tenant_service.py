from fastapi import HTTPException

from src.core.constants import (
    HTTP_BAD_REQUEST,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND,
)
from src.core.storage import UnitOfWork
from src.repositories.sys.user_repository import user_repository
from src.repositories.sys.user_tenant_repository import user_tenant_repository
from src.schemas.sys.user_tenant import TenantCreate


class UserTenantService:
    def __init__(self):
        self.repository = user_tenant_repository

    def get_user_tenants(self, user_id: int) -> list[dict]:
        with UnitOfWork() as uow:
            tenants = self.repository.get_user_tenants(user_id, session=uow.session)
            uow.commit()
            return tenants

    def get_tenant_members(self, tenant_id: int) -> list[dict]:
        with UnitOfWork() as uow:
            members = self.repository.get_tenant_members(tenant_id, session=uow.session)
            uow.commit()
            return members

    def check_user_in_tenant(self, user_id: int, tenant_id: int) -> bool:
        with UnitOfWork() as uow:
            result = self.repository.is_user_in_tenant(user_id, tenant_id, session=uow.session)
            uow.commit()
            return result

    def check_tenant_owner(self, user_id: int, tenant_id: int) -> bool:
        with UnitOfWork() as uow:
            result = self.repository.is_tenant_owner(user_id, tenant_id, session=uow.session)
            uow.commit()
            return result

    def create_tenant(self, tenant_in: TenantCreate, owner_user_id: int) -> dict:
        with UnitOfWork() as uow:
            owner = user_repository.get(id=owner_user_id, session=uow.session)
            if not owner:
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="用户不存在")

            existing_tenant = self.repository.get_tenant_by_code(tenant_in.code, session=uow.session)
            if existing_tenant:
                raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="租户编码已存在")

            tenant_data = tenant_in.model_dump(exclude={"role_ids"})
            tenant_data["owner_user_id"] = owner_user_id

            tenant = self.repository.create_tenant_with_owner(
                tenant_data=tenant_data,
                owner_user_id=owner_user_id,
                session=uow.session
            )

            uow.commit()

            return {
                "id": tenant.id,
                "name": tenant.name,
                "code": tenant.code,
                "owner_user_id": tenant.owner_user_id,
                "created_at": tenant.created_at
            }

    def invite_user_to_tenant(
        self,
        tenant_id: int,
        user_id: int,
        inviter_user_id: int
    ) -> dict:
        with UnitOfWork() as uow:
            inviter = user_repository.get(id=inviter_user_id, session=uow.session)
            if not inviter:
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="邀请人不存在")

            if not self.repository.is_user_in_tenant(inviter_user_id, tenant_id, session=uow.session):
                if not self.repository.is_tenant_owner(inviter_user_id, tenant_id, session=uow.session):
                    raise HTTPException(status_code=HTTP_FORBIDDEN, detail="只有租户成员可以邀请新成员")

            user = user_repository.get(id=user_id, session=uow.session)
            if not user:
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="被邀请用户不存在")

            if self.repository.is_user_in_tenant(user_id, tenant_id, session=uow.session):
                raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="用户已在租户中")

            self.repository.add_user_to_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
                is_owner=False,
                session=uow.session
            )

            uow.commit()

            return {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "is_owner": False
            }

    def remove_user_from_tenant(self, tenant_id: int, user_id: int, operator_user_id: int) -> bool:
        with UnitOfWork() as uow:
            if not self.repository.is_tenant_owner(operator_user_id, tenant_id, session=uow.session):
                raise HTTPException(status_code=HTTP_FORBIDDEN, detail="只有户主可以移除成员")

            if self.repository.is_tenant_owner(user_id, tenant_id, session=uow.session):
                raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="不能移除租户户主")

            success = self.repository.remove_user_from_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
                session=uow.session
            )

            if not success:
                raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="用户不在此租户中")

            uow.commit()
            return True

    def get_user_current_tenant(self, user_id: int, tenant_id: int) -> dict:
        with UnitOfWork() as uow:
            relation = self.repository.get_user_tenant_relation(user_id, tenant_id, session=uow.session)
            uow.commit()

            if not relation:
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="用户不在此租户中")

            return relation


user_tenant_service = UserTenantService()
