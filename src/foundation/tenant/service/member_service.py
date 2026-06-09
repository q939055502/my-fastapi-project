from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.storage import TransactionManager
from src.foundation.platform.repository.user_repository import user_repository
from src.foundation.tenant.repository.member_repository import tenant_member_repository
from src.foundation.tenant.schemas.tenant import TenantCreate


class UserTenantService:
    def __init__(self):
        self.repository = tenant_member_repository

    def get_user_tenants(self, user_id: int) -> list[dict]:
        with TransactionManager() as tm:
            tenants = self.repository.get_user_tenants(user_id, session=tm.session)
            tm.commit()
            return tenants

    def get_tenant_members(self, tenant_id: int) -> list[dict]:
        with TransactionManager() as tm:
            members = self.repository.get_tenant_members(tenant_id, session=tm.session)
            tm.commit()
            return members

    def check_user_in_tenant(self, user_id: int, tenant_id: int) -> bool:
        with TransactionManager() as tm:
            result = self.repository.is_user_in_tenant(user_id, tenant_id, session=tm.session)
            tm.commit()
            return result

    def check_tenant_owner(self, user_id: int, tenant_id: int) -> bool:
        with TransactionManager() as tm:
            result = self.repository.is_tenant_owner(user_id, tenant_id, session=tm.session)
            tm.commit()
            return result

    def create_tenant(self, tenant_in: TenantCreate, owner_user_id: int) -> dict:
        with TransactionManager() as tm:
            owner = user_repository.get(id=owner_user_id, session=tm.session)
            if not owner:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "用户不存在")

            existing_tenant = self.repository.get_tenant_by_code(tenant_in.code, session=tm.session)
            if existing_tenant:
                raise BusinessException(ResponseCode.PARAM_ERROR, "租户编码已存在")

            tenant_data = tenant_in.model_dump(exclude={"role_ids"})
            tenant_data["owner_user_id"] = owner_user_id

            tenant = self.repository.create_tenant_with_owner(
                tenant_data=tenant_data,
                owner_user_id=owner_user_id,
                session=tm.session
            )

            tm.commit()

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
        with TransactionManager() as tm:
            inviter = user_repository.get(id=inviter_user_id, session=tm.session)
            if not inviter:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "邀请人不存在")

            if not self.repository.is_user_in_tenant(inviter_user_id, tenant_id, session=tm.session):
                if not self.repository.is_tenant_owner(inviter_user_id, tenant_id, session=tm.session):
                    raise BusinessException(ResponseCode.FORBIDDEN, "只有租户成员可以邀请新成员")

            user = user_repository.get(id=user_id, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "被邀请用户不存在")

            if self.repository.is_user_in_tenant(user_id, tenant_id, session=tm.session):
                raise BusinessException(ResponseCode.PARAM_ERROR, "用户已在租户中")

            self.repository.add_user_to_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
                is_owner=False,
                session=tm.session
            )

            tm.commit()

            return {
                "user_id": user_id,
                "tenant_id": tenant_id,
                "is_owner": False
            }

    def remove_user_from_tenant(self, tenant_id: int, user_id: int, operator_user_id: int) -> bool:
        with TransactionManager() as tm:
            if not self.repository.is_tenant_owner(operator_user_id, tenant_id, session=tm.session):
                raise BusinessException(ResponseCode.FORBIDDEN, "只有户主可以移除成员")

            if self.repository.is_tenant_owner(user_id, tenant_id, session=tm.session):
                raise BusinessException(ResponseCode.PARAM_ERROR, "不能移除租户户主")

            success = self.repository.remove_user_from_tenant(
                user_id=user_id,
                tenant_id=tenant_id,
                session=tm.session
            )

            if not success:
                raise BusinessException(ResponseCode.PARAM_ERROR, "用户不在此租户中")

            tm.commit()
            return True

    def get_user_current_tenant(self, user_id: int, tenant_id: int) -> dict:
        with TransactionManager() as tm:
            relation = self.repository.get_user_tenant_relation(user_id, tenant_id, session=tm.session)
            tm.commit()

            if not relation:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "用户不在此租户中")

            return relation


user_tenant_service = UserTenantService()
