from uuid import UUID

from sqlalchemy import asc
from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.storage import TransactionManager
from src.foundation.platform.repository.role_permission_repository import role_permission_repository
from src.foundation.platform.repository.role_repository import role_repository
from src.foundation.platform.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self):
        self.repository = role_repository

    def get_role_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
        remark: str = "",
    ) -> tuple[int, list[dict]]:
        with TransactionManager() as tm:
            search_filters = self._build_role_search_filters(
                name=name, remark=remark
            )

            total, items = self.repository.list(
                page=page,
                page_size=page_size,
                session=tm.session,
                filters=search_filters,
                order_by=[asc(self.repository.model.id)],
            )

            data = self._transform_role_list(items)

            return total, data

    def get_role_detail(self, role_uuid: UUID) -> dict:
        with TransactionManager() as tm:
            role_obj = role_repository.get_by_uuid(uuid=role_uuid, session=tm.session)
            if not role_obj:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="角色/职位不存在")

            role_dict = {}
            for column in role_obj.__table__.columns:
                field_name = column.name
                value = getattr(role_obj, field_name)
                role_dict[field_name] = value

            role_dict["permissions"] = []
            role_perms = role_permission_repository.get_by_role_id(role_obj.id, tm.session)
            
            for role_perm in role_perms:
                permission = role_perm.permission
                if permission:
                    permission_dict = {
                        "uuid": permission.uuid,
                        "name": permission.name,
                        "resource": permission.resource,
                        "action": permission.action,
                        "scope": permission.scope,
                        "type": permission.type,
                    }
                    role_dict["permissions"].append(permission_dict)

            return role_dict

    def create_role(self, role_in: RoleCreate) -> None:
        with TransactionManager() as tm:
            if getattr(role_in, "is_system", False):
                raise BusinessException(
                    ResponseCode.FORBIDDEN,
                    detail="禁止创建系统内置角色/职位",
                )

            existing_role = role_repository.is_exist(role_in.name, session=tm.session)
            if existing_role:
                raise BusinessException(
                    ResponseCode.PARAM_ERROR,
                    detail="该角色/职位名称已存在",
                )

            role_repository.create(obj_in=role_in, session=tm.session)

            tm.commit()

    def update_role(self, role_uuid: UUID, role_in: RoleUpdate) -> None:
        with TransactionManager() as tm:
            existing_role = role_repository.get_by_uuid(uuid=role_uuid, session=tm.session)
            if not existing_role:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="角色/职位不存在")

            if existing_role.is_system:
                raise BusinessException(
                    ResponseCode.FORBIDDEN,
                    detail="系统内置角色/职位不可修改",
                )

            if role_in.name != existing_role.name:
                existing_by_name = role_repository.is_exist(role_in.name, session=tm.session)
                if existing_by_name:
                    raise BusinessException(
                        ResponseCode.PARAM_ERROR,
                        detail="该角色/职位名称已存在",
                    )

            role_repository.update(id=existing_role.id, obj_in=role_in, session=tm.session)
            tm.commit()

    def update_role_permissions(self, role_uuid: UUID, permission_uuids: list[UUID]) -> None:
        with TransactionManager() as tm:
            role_obj = role_repository.get_by_uuid(uuid=role_uuid, session=tm.session)
            if not role_obj:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="角色/职位不存在")

            if role_obj.is_system:
                raise BusinessException(
                    ResponseCode.FORBIDDEN,
                    detail="系统内置角色/职位不可修改权限",
                )

            role_repository.update_permissions(role_obj, permission_uuids, session=tm.session)
            tm.commit()

    def delete_role(self, role_uuid: UUID) -> None:
        with TransactionManager() as tm:
            existing_role = role_repository.get_by_uuid(uuid=role_uuid, session=tm.session)
            if not existing_role:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="角色/职位不存在")

            if existing_role.is_system:
                raise BusinessException(
                    ResponseCode.FORBIDDEN,
                    detail="系统内置角色/职位不可删除",
                )

            role_repository.delete(id=existing_role.id, session=tm.session)

            tm.commit()

    def _build_role_search_filters(
        self,
        name: str = "",
        remark: str = "",
    ) -> list:
        filters = []

        if name:
            filters.append(self.repository.model.name.contains(name))

        if remark:
            filters.append(self.repository.model.remark.contains(remark))

        return filters

    def _transform_role_list(self, items) -> list[dict]:
        data = []

        for obj in items:
            role_dict = {}
            for column in obj.__table__.columns:
                field_name = column.name
                value = getattr(obj, field_name)
                role_dict[field_name] = value

            role_dict["menu_count"] = len([
                rp for rp in obj.role_permissions 
                if rp.permission and rp.permission.type == "menu"
            ])
            role_dict["api_count"] = len([
                rp for rp in obj.role_permissions 
                if rp.permission and rp.permission.type == "api"
            ])

            data.append(role_dict)

        return data


role_service = RoleService()