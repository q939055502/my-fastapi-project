from src.core.constants import (
    HTTP_BAD_REQUEST,
    HTTP_NOT_FOUND,
)
from src.core.storage import TransactionManager
from src.repositories.sys.resource_repository import resource_repository
from src.schemas.sys.resource import ResourceCreate, ResourceUpdate


class ResourceService:
    pass

    def get_resource_detail(self, resource_id: int):
        with TransactionManager() as tm:
            resource = resource_repository.get_by_id(resource_id, tm.session)
            if not resource:
                from fastapi.exceptions import HTTPException
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="资源不存在")
            return self._transform_resource(resource)

    def get_resource_list(self, type: int | None = None, name: str = "", page: int = 1, page_size: int = 10):
        with TransactionManager() as tm:
            filters = []
            if type:
                filters.append(resource_repository.model.type == type)
            if name:
                filters.append(resource_repository.model.name.contains(name))

            total, resources = resource_repository.list(
                page=page,
                page_size=page_size,
                session=tm.session,
                filters=filters,
                order_by=[resource_repository.model.sort.asc()]
            )
            return total, [self._transform_resource(r) for r in resources]

    def create_resource(self, resource_in: ResourceCreate):
        with TransactionManager() as tm:
            if resource_repository.exists_by_code(resource_in.code, session=tm.session):
                from fastapi.exceptions import HTTPException
                raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="资源编码已存在")

            resource_data = resource_in.model_dump()
            resource = resource_repository.create(resource_data, tm.session)
            tm.commit()
            return self._transform_resource(resource)

    def update_resource(self, resource_id: int, resource_in: ResourceUpdate):
        with TransactionManager() as tm:
            if resource_in.code and resource_repository.exists_by_code(resource_in.code, exclude_id=resource_id, session=tm.session):
                from fastapi.exceptions import HTTPException
                raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="资源编码已存在")

            resource = resource_repository.update(resource_id, resource_in.model_dump(exclude_unset=True), tm.session)
            if not resource:
                from fastapi.exceptions import HTTPException
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="资源不存在")
            tm.commit()
            return self._transform_resource(resource)

    def delete_resource(self, resource_id: int):
        with TransactionManager() as tm:
            success = resource_repository.delete(resource_id, tm.session)
            if not success:
                from fastapi.exceptions import HTTPException
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="资源不存在")
            tm.commit()

    def get_resource_types(self):
        return [
            {"type": 1, "name": "菜单", "remark": "前端导航菜单"},
            {"type": 2, "name": "API", "remark": "后端接口"},
            {"type": 3, "name": "按钮", "remark": "页面按钮"}
        ]

    def _transform_resource(self, resource):
        resource_dict = {
            "id": resource.id,
            "code": resource.code,
            "name": resource.name,
            "type": resource.type,
            "api_path": resource.api_path,
            "api_method": resource.api_method,
            "path": resource.path,
            "icon": resource.icon,
            "parent_id": resource.parent_id,
            "sort": resource.sort,
            "status": resource.status,
            "remark": resource.remark,
            "created_at": resource.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": resource.updated_at.strftime("%Y-%m-%d %H:%M:%S") if resource.updated_at else None
        }

        return resource_dict


resource_service = ResourceService()
