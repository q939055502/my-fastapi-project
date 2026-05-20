from fastapi.exceptions import HTTPException

from src.repositories.sys.role_repository import role_repository
from src.schemas.sys.roles import RoleCreate, RoleUpdate
from src.core.log import logger
from src.core.storage import UnitOfWork
from sqlalchemy import asc


class RoleService:
    def __init__(self):
        self.repository = role_repository
        self.logger = logger

    def get_role_list(
        self,
        page: int = 1,
        page_size: int = 10,
        name: str = "",
        remark: str = "",
    ) -> tuple[int, list[dict]]:
        with UnitOfWork() as uow:
            search_filters = self._build_role_search_filters(
                name=name, remark=remark
            )

            total, items = self.repository.list(
                page=page,
                page_size=page_size,
                session=uow.session,
                filters=search_filters,
                order_by=[asc(self.repository.model.id)],
            )

            data = self._transform_role_list(items)

            return total, data

    def get_role_detail(self, role_id: int) -> dict:
        with UnitOfWork() as uow:
            role_obj = role_repository.get(id=role_id, session=uow.session)
            if not role_obj:
                raise HTTPException(status_code=404, detail="角色不存在")

            role_dict = {}
            for column in role_obj.__table__.columns:
                field_name = column.name
                value = getattr(role_obj, field_name)
                role_dict[field_name] = value

            role_dict["resources"] = []
            for resource in role_obj.resources:
                resource_dict = {
                    "id": resource.id,
                    "name": resource.name,
                    "type": resource.type,
                    "api_path": resource.api_path,
                    "api_method": resource.api_method,
                    "path": resource.path,
                    "icon": resource.icon,
                    "code": resource.code,
                }
                role_dict["resources"].append(resource_dict)

            return role_dict

    def create_role(self, role_in: RoleCreate) -> None:
        with UnitOfWork() as uow:
            if getattr(role_in, "is_system", False):
                raise HTTPException(
                    status_code=403,
                    detail="禁止创建系统内置角色",
                )

            existing_role = role_repository.is_exist(role_in.name, session=uow.session)
            if existing_role:
                raise HTTPException(
                    status_code=400,
                    detail="The role with this name already exists in the system.",
                )

            role_repository.create(obj_in=role_in, session=uow.session)

            uow.commit()

    def update_role(self, role_id: int, role_in: RoleUpdate) -> None:
        with UnitOfWork() as uow:
            existing_role = role_repository.get(id=role_id, session=uow.session)
            if not existing_role:
                raise HTTPException(status_code=404, detail="角色不存在")

            if existing_role.is_system:
                raise HTTPException(
                    status_code=403,
                    detail="系统内置角色不可修改",
                )

            if role_in.name != existing_role.name:
                existing_by_name = role_repository.is_exist(role_in.name, session=uow.session)
                if existing_by_name:
                    raise HTTPException(
                        status_code=400,
                        detail="The role name already exists in the system.",
                    )

            role_repository.update(id=role_id, obj_in=role_in, session=uow.session)
            uow.commit()

    def update_role_resources(self, role_id: int, resource_ids: list[int]) -> None:
        with UnitOfWork() as uow:
            role_obj = role_repository.get(id=role_id, session=uow.session)
            if not role_obj:
                raise HTTPException(status_code=404, detail="角色不存在")

            if role_obj.is_system:
                raise HTTPException(
                    status_code=403,
                    detail="系统内置角色不可修改权限",
                )

            role_repository.update_resources(role_obj, resource_ids, session=uow.session)
            uow.commit()

    def delete_role(self, role_id: int) -> None:
        with UnitOfWork() as uow:
            existing_role = role_repository.get(id=role_id, session=uow.session)
            if not existing_role:
                raise HTTPException(status_code=404, detail="角色不存在")

            if existing_role.is_system:
                raise HTTPException(
                    status_code=403,
                    detail="系统内置角色不可删除",
                )

            role_repository.delete(id=role_id, session=uow.session)

            uow.commit()

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

            role_dict["menu_count"] = len([r for r in obj.resources if r.type == 1])
            role_dict["api_count"] = len([r for r in obj.resources if r.type == 2])

            data.append(role_dict)

        return data


role_service = RoleService()
