"""
权限控制模块

处理API权限控制相关的逻辑,检查用户是否有访问指定API的权限。
"""

import re

from fastapi import Depends, Request

from src.core.constants import RoleCodeConst
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager
from src.foundation.iam.auth.dependency import AuthControl
from src.foundation.iam.rbac.repository.permission_repository import (
    permission_repository,
)
from src.foundation.iam.rbac.repository.role_repository import role_repository
from src.foundation.iam.rbac.repository.role_subject_repository import (
    role_subject_repository,
)


class PermissionControl:
    """权限控制类
    处理API权限控制相关的逻辑,检查用户是否有访问指定API的权限。
    """

    @classmethod
    def has_permission(
        cls,
        request: Request,
        permission_code: str = None,
        current_user: object = Depends(AuthControl.is_authed),
    ) -> None:
        """检查用户是否有访问指定API的权限

        Args:
            request: FastAPI请求对象
            permission_code: 权限编码(可选,用于精确权限校验)
            current_user: 当前认证用户

        Raises:
            HTTPException: 当用户无权限时抛出403错误
        """
        with TransactionManager() as tm:
            auth_ctx = getattr(request.state, "auth_context", None)
            if auth_ctx:
                role_ids = role_subject_repository.get_role_ids_by_subject(
                    subject_id=auth_ctx.subject_id,
                    subject_type=auth_ctx.subject_type,
                    session=tm.session
                )
                roles = role_repository.list_by_ids(role_ids=role_ids, session=tm.session)
            else:
                roles = getattr(current_user, 'roles', [])

        if roles:
            for role in roles:
                if role.code == RoleCodeConst.PLATFORM_SUPER_ADMIN.value:
                    return

        if permission_code:
            cls._check_permission_code(request, permission_code)
            return

        method = request.method
        path = request.url.path

        if not roles:
            raise BusinessException(40300, "用户未绑定角色")

        all_resources = []
        for role in roles:
            all_resources.extend(getattr(role, 'resources', []))

        for resource in all_resources:
            if getattr(resource, 'api_method', None) == method and getattr(resource, 'api_path', None) is not None:
                pattern = re.sub(r"\{[^}]+\}", r"[^/]+", resource.api_path)
                pattern = f"^{pattern}$"
                if re.match(pattern, path):
                    return

        raise BusinessException(40300, "无此API访问权限")

    @classmethod
    def _check_permission_code(cls, request: Request, permission_code: str) -> None:
        """检查指定的权限编码

        Args:
            request: FastAPI请求对象
            permission_code: 权限编码

        Raises:
            HTTPException: 当用户无权限时抛出403错误
        """
        auth_ctx = getattr(request.state, "auth_context", None)

        if not auth_ctx:
            raise BusinessException(40300, "无权限")

        if permission_code.startswith("platform:"):
            if auth_ctx.subject_type != 0:
                raise BusinessException(40300, "无平台权限")
        elif permission_code.startswith("tenant:"):
            if auth_ctx.subject_type != 1:
                raise BusinessException(40300, "无租户权限")

        with TransactionManager() as tm:
            role_ids = role_subject_repository.get_role_ids_by_subject(
                subject_id=auth_ctx.subject_id,
                subject_type=auth_ctx.subject_type,
                session=tm.session
            )
            roles = role_repository.list_by_ids(role_ids=role_ids, session=tm.session)

            if not roles:
                raise BusinessException(40300, "无此权限")

            for role in roles:
                permissions = permission_repository.get_permissions_by_role(
                    role.id, tm.session
                )
                for perm in permissions:
                    perm_code = f"{perm.resource}:{perm.action}"
                    if perm_code == permission_code:
                        return

        raise BusinessException(40300, "无此权限")
