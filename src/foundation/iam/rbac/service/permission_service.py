from typing import Any

from src.core.exceptions import BusinessException
from src.core.log import logger
from src.core.storage import TransactionManager
from src.foundation.iam.rbac.repository.permission_repository import (
    permission_repository,
)


class PermissionService:
    def create_permission(self, resource: str, action: str, description: str = None, scope: str = None, session=None) -> dict[str, Any]:
        if permission_repository.get_by_resource_and_action(resource, action, session=session):
            raise BusinessException(40000, "权限已存在")

        with TransactionManager(session=session) as tm:
            permission = permission_repository.create(
                obj_in={
                    "resource": resource,
                    "action": action,
                    "description": description,
                    "scope": scope,
                },
                session=tm.session,
            )
            tm.commit()

        logger.info(f"创建权限: resource={resource}, action={action}")
        return {
            "permission_id": permission.id,
            "resource": permission.resource,
            "action": permission.action,
        }

    def update_permission(self, permission_id: int, description: str = None, scope: str = None, session=None) -> dict[str, Any]:
        with TransactionManager(session=session) as tm:
            permission = permission_repository.get(id=permission_id, session=tm.session)
            if not permission:
                raise BusinessException(40400, "权限不存在")

            update_data = {}
            if description is not None:
                update_data["description"] = description
            if scope is not None:
                update_data["scope"] = scope

            if update_data:
                permission = permission_repository.update(db_obj=permission, obj_in=update_data, session=tm.session)
                tm.commit()

        logger.info(f"更新权限: permission_id={permission_id}")
        return {
            "permission_id": permission.id,
            "resource": permission.resource,
            "action": permission.action,
            "description": permission.description,
            "scope": permission.scope,
        }

    def delete_permission(self, permission_id: int, session=None) -> None:
        with TransactionManager(session=session) as tm:
            permission = permission_repository.get(id=permission_id, session=tm.session)
            if not permission:
                raise BusinessException(40400, "权限不存在")

            permission_repository.remove(db_obj=permission, session=tm.session)
            tm.commit()

        logger.info(f"删除权限: permission_id={permission_id}")

    def list_permissions(self, resource: str = None, scope: str = None, session=None) -> list[dict[str, Any]]:
        if resource:
            permissions = permission_repository.get_by_resource(resource, session=session)
        elif scope:
            permissions = permission_repository.list_by_scope(scope, session=session)
        else:
            permissions = permission_repository.list(session=session)

        return [
            {
                "id": perm.id,
                "resource": perm.resource,
                "action": perm.action,
                "description": perm.description,
                "scope": perm.scope,
            }
            for perm in permissions
        ]

    def get_permission(self, permission_id: int, session=None) -> dict[str, Any]:
        permission = permission_repository.get(id=permission_id, session=session)
        if not permission:
            raise BusinessException(40400, "权限不存在")

        return {
            "id": permission.id,
            "resource": permission.resource,
            "action": permission.action,
            "description": permission.description,
            "scope": permission.scope,
        }


permission_service = PermissionService()
