from typing import Any

from src.core.constants import RoleCodeConst
from src.core.exceptions import BusinessException
from src.core.log import logger
from src.core.storage import TransactionManager
from src.foundation.iam.rbac.repository.permission_repository import (
    permission_repository,
)
from src.foundation.iam.rbac.repository.role_permission_repository import (
    role_permission_repository,
)
from src.foundation.iam.rbac.repository.role_repository import role_repository
from src.foundation.iam.rbac.repository.role_subject_repository import (
    role_subject_repository,
)


class RoleService:
    def create_platform_role(self, name: str, code: str, description: str = None, session=None) -> dict[str, Any]:
        if role_repository.check_role_exists(name, tenant_id=None, session=session):
            raise BusinessException(40000, "角色名称已存在")

        if role_repository.get_by_code(code, session=session):
            raise BusinessException(40000, "角色编码已存在")

        with TransactionManager(session=session) as tm:
            role = role_repository.create(
                obj_in={
                    "name": name,
                    "code": code,
                    "description": description,
                    "tenant_id": None,
                    "is_platform": True,
                },
                session=tm.session,
            )
            tm.commit()

        logger.info(f"创建平台角色: name={name}, code={code}")
        return {"role_id": role.id, "name": role.name, "code": role.code}

    def create_tenant_role(self, name: str, description: str = None, tenant_id: int = None, session=None) -> dict[str, Any]:
        if role_repository.check_role_exists(name, tenant_id=tenant_id, session=session):
            raise BusinessException(40000, "角色名称已存在")

        with TransactionManager(session=session) as tm:
            role = role_repository.create(
                obj_in={
                    "name": name,
                    "description": description,
                    "tenant_id": tenant_id,
                    "is_platform": False,
                },
                session=tm.session,
            )
            tm.commit()

        logger.info(f"创建租户角色: name={name}, tenant_id={tenant_id}")
        return {"role_id": role.id, "name": role.name}

    def update_role(self, role_id: int, name: str = None, description: str = None, session=None) -> dict[str, Any]:
        with TransactionManager(session=session) as tm:
            role = role_repository.get(id=role_id, session=tm.session)
            if not role:
                raise BusinessException(40400, "角色不存在")

            if role.code in [RoleCodeConst.PLATFORM_SUPER_ADMIN.value, RoleCodeConst.PLATFORM_NORMAL_USER.value]:
                raise BusinessException(40300, "系统内置角色不可修改")

            update_data = {}
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description

            if update_data:
                role = role_repository.update(db_obj=role, obj_in=update_data, session=tm.session)
                tm.commit()

        logger.info(f"更新角色: role_id={role_id}, name={role.name}")
        return {"role_id": role.id, "name": role.name}

    def delete_role(self, role_id: int, session=None) -> None:
        with TransactionManager(session=session) as tm:
            role = role_repository.get(id=role_id, session=tm.session)
            if not role:
                raise BusinessException(40400, "角色不存在")

            if role.code in [RoleCodeConst.PLATFORM_SUPER_ADMIN.value, RoleCodeConst.PLATFORM_NORMAL_USER.value]:
                raise BusinessException(40300, "系统内置角色不可删除")

            role_permission_repository.remove_by_role(role_id, session=tm.session)
            role_repository.remove(db_obj=role, session=tm.session)
            tm.commit()

        logger.info(f"删除角色: role_id={role_id}, name={role.name}")

    def assign_permissions(self, role_id: int, permission_ids: list[int], session=None) -> None:
        with TransactionManager(session=session) as tm:
            role = role_repository.get(id=role_id, session=tm.session)
            if not role:
                raise BusinessException(40400, "角色不存在")

            role_permission_repository.batch_create(role_id, permission_ids, session=tm.session)
            tm.commit()

        logger.info(f"为角色分配权�? role_id={role_id}, permission_count={len(permission_ids)}")

    def remove_permissions(self, role_id: int, permission_ids: list[int], session=None) -> None:
        with TransactionManager(session=session) as tm:
            role = role_repository.get(id=role_id, session=tm.session)
            if not role:
                raise BusinessException(40400, "角色不存在")

            role_permission_repository.batch_remove(role_id, permission_ids, session=tm.session)
            tm.commit()

        logger.info(f"移除角色权限: role_id={role_id}, permission_count={len(permission_ids)}")

    def assign_role_to_subject(self, role_id: int, subject_ids: list[int], subject_type: int, session=None) -> None:
        with TransactionManager(session=session) as tm:
            role = role_repository.get(id=role_id, session=tm.session)
            if not role:
                raise BusinessException(40400, "角色不存在")

            role_subject_repository.batch_create(role_id, subject_ids, subject_type, session=tm.session)
            tm.commit()

        logger.info(f"为主体分配角色: role_id={role_id}, subject_type={subject_type}, subject_count={len(subject_ids)}")

    def remove_role_from_subject(self, role_id: int, subject_ids: list[int], subject_type: int, session=None) -> None:
        with TransactionManager(session=session) as tm:
            role = role_repository.get(id=role_id, session=tm.session)
            if not role:
                raise BusinessException(40400, "角色不存在")

            role_subject_repository.batch_remove(role_id, subject_ids, subject_type, session=tm.session)
            tm.commit()

        logger.info(f"移除主体角色: role_id={role_id}, subject_type={subject_type}, subject_count={len(subject_ids)}")

    def get_role_permissions(self, role_id: int, session=None) -> list[dict[str, Any]]:
        permissions = permission_repository.get_permissions_by_role(role_id, session=session)
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


role_service = RoleService()
