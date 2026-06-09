from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.storage import TransactionManager
from src.foundation.platform.repository.permission_repository import permission_repository
from src.foundation.platform.schemas.permission import PermissionCreate, PermissionUpdate


class ResourceService:
    def get_resource_detail(self, resource_id: int):
        with TransactionManager() as tm:
            resource = permission_repository.get_by_id(resource_id, tm.session)
            if not resource:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="资源不存在")
            return self._transform_resource(resource)

    def get_resource_list(self, type: str | None = None, name: str = "", page: int = 1, page_size: int = 10):
        with TransactionManager() as tm:
            filters = []
            if type:
                filters.append(permission_repository.model.type == type)
            if name:
                filters.append(permission_repository.model.name.contains(name))

            total, resources = permission_repository.list(
                page=page,
                page_size=page_size,
                session=tm.session,
                filters=filters,
                order_by=[permission_repository.model.sort.asc()]
            )
            return total, [self._transform_resource(r) for r in resources]

    def create_resource(self, resource_in: PermissionCreate):
        with TransactionManager() as tm:
            if permission_repository.exists_by_code(resource_in.code, session=tm.session):
                raise BusinessException(ResponseCode.PARAM_ERROR, detail="资源编码已存在")

            resource_data = resource_in.model_dump()
            resource = permission_repository.create(resource_data, tm.session)
            tm.commit()
            return self._transform_resource(resource)

    def update_resource(self, resource_id: int, resource_in: PermissionUpdate):
        with TransactionManager() as tm:
            if resource_in.code and permission_repository.exists_by_code(resource_in.code, exclude_id=resource_id, session=tm.session):
                raise BusinessException(ResponseCode.PARAM_ERROR, detail="资源编码已存在")

            resource = permission_repository.update(resource_id, resource_in.model_dump(exclude_unset=True), tm.session)
            if not resource:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="资源不存在")
            tm.commit()
            return self._transform_resource(resource)

    def delete_resource(self, resource_id: int):
        with TransactionManager() as tm:
            success = permission_repository.delete(resource_id, tm.session)
            if not success:
                raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, detail="资源不存在")
            tm.commit()

    def get_resource_types(self):
        return [
            {"type": "menu", "name": "菜单", "remark": "前端导航菜单"},
            {"type": "api", "name": "API", "remark": "后端接口"},
            {"type": "button", "name": "按钮", "remark": "页面按钮"}
        ]

    def _transform_resource(self, resource):
        resource_dict = {
            "id": resource.id,
            "code": resource.code,
            "name": resource.name,
            "type": resource.type,
            "parent_id": resource.parent_id,
            "sort": resource.sort,
            "remark": resource.remark,
            "created_at": resource.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": resource.updated_at.strftime("%Y-%m-%d %H:%M:%S") if resource.updated_at else None
        }

        return resource_dict


resource_service = ResourceService()
