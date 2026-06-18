from uuid import UUID

from src.core.enums.response_code import ResponseCode
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.system.repository.user_repository import user_repository
from src.foundation.tenant.repository.member_repository import tenant_member_repository
from src.foundation.tenant.repository.tenant_repository import tenant_repository
from src.foundation.tenant.schemas.tenant import TenantCreate


class UserTenantService:
    def __init__(self):
        self.repository = tenant_member_repository

    def get_user_tenants(self, user_uuid: UUID) -> list[dict]:
        with TransactionManager() as tm:
            user = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            if not user:
                return []
            tenants = self.repository.get_user_tenants(user.id, session=tm.session)
            tm.commit()
            return tenants

    def get_tenant_members(self, tenant_uuid: UUID) -> list[dict]:
        with TransactionManager() as tm:
            tenant = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=tm.session)
            if not tenant:
                return []
            members = self.repository.get_tenant_members(tenant.id, session=tm.session)
            tm.commit()
            return members

    def check_user_in_tenant(self, user_uuid: UUID, tenant_uuid: UUID) -> bool:
        with TransactionManager() as tm:
            user = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            tenant = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=tm.session)
            if not user or not tenant:
                return False
            result = self.repository.is_user_in_tenant(user.id, tenant.id, session=tm.session)
            tm.commit()
            return result

    def check_tenant_owner(self, user_uuid: UUID, tenant_uuid: UUID) -> bool:
        with TransactionManager() as tm:
            user = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            tenant = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=tm.session)
            if not user or not tenant:
                return False
            result = self.repository.is_tenant_owner(user.id, tenant.id, session=tm.session)
            tm.commit()
            return result

    def create_tenant(self, tenant_in: TenantCreate, owner_user_uuid: UUID) -> dict:
        with TransactionManager() as tm:
            owner = user_repository.get_by_uuid(uuid=owner_user_uuid, session=tm.session)
            if not owner:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "用户不存在")

            existing_tenant = self.repository.get_tenant_by_code(tenant_in.code, session=tm.session)
            if existing_tenant:
                raise BusinessException(ResponseCode.PARAM_ERROR, "租户编码已存在")

            tenant_data = tenant_in.model_dump(exclude={"owner_user_uuid"})
            tenant_data["owner_user_id"] = owner.id

            tenant = self.repository.create_tenant_with_owner(
                tenant_data=tenant_data,
                owner_user_id=owner.id,
                session=tm.session
            )

            tm.commit()

            return {
                "uuid": tenant.uuid,
                "name": tenant.name,
                "code": tenant.code,
                "owner_user_uuid": owner_user_uuid,
                "created_at": tenant.created_at
            }

    def invite_user_to_tenant(
        self,
        tenant_uuid: UUID,
        user_uuid: UUID,
        inviter_user_uuid: UUID
    ) -> dict:
        with TransactionManager() as tm:
            inviter = user_repository.get_by_uuid(uuid=inviter_user_uuid, session=tm.session)
            if not inviter:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "邀请人不存在")

            tenant = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=tm.session)
            if not tenant:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "租户不存在")

            if not self.repository.is_user_in_tenant(inviter.id, tenant.id, session=tm.session):
                if not self.repository.is_tenant_owner(inviter.id, tenant.id, session=tm.session):
                    raise BusinessException(ResponseCode.FORBIDDEN, "只有租户成员可以邀请新成员")

            user = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "被邀请用户不存在")

            if self.repository.is_user_in_tenant(user.id, tenant.id, session=tm.session):
                raise BusinessException(ResponseCode.PARAM_ERROR, "用户已在租户中")

            self.repository.add_user_to_tenant(
                user_id=user.id,
                tenant_id=tenant.id,
                is_owner=False,
                session=tm.session
            )

            tm.commit()

            return {
                "user_uuid": user_uuid,
                "tenant_uuid": tenant_uuid,
                "is_owner": False
            }

    def remove_user_from_tenant(self, tenant_uuid: UUID, user_uuid: UUID, operator_user_uuid: UUID) -> bool:
        with TransactionManager() as tm:
            tenant = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=tm.session)
            if not tenant:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "租户不存在")

            operator = user_repository.get_by_uuid(uuid=operator_user_uuid, session=tm.session)
            if not operator:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "操作人不存在")

            user = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "用户不存在")

            if not self.repository.is_tenant_owner(operator.id, tenant.id, session=tm.session):
                raise BusinessException(ResponseCode.FORBIDDEN, "只有户主可以移除成员")

            if self.repository.is_tenant_owner(user.id, tenant.id, session=tm.session):
                raise BusinessException(ResponseCode.PARAM_ERROR, "不能移除租户户主")

            success = self.repository.remove_user_from_tenant(
                user_id=user.id,
                tenant_id=tenant.id,
                session=tm.session
            )

            if not success:
                raise BusinessException(ResponseCode.PARAM_ERROR, "用户不在此租户中")

            tm.commit()
            return True

    def get_user_current_tenant(self, user_uuid: UUID, tenant_uuid: UUID) -> dict:
        with TransactionManager() as tm:
            user = user_repository.get_by_uuid(uuid=user_uuid, session=tm.session)
            tenant = tenant_repository.get_by_uuid(uuid=tenant_uuid, session=tm.session)
            if not user or not tenant:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "用户或租户不存在")

            relation = self.repository.get_user_tenant_relation(user.id, tenant.id, session=tm.session)
            tm.commit()

            if not relation:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "用户不在此租户中")

            return relation


user_tenant_service = UserTenantService()