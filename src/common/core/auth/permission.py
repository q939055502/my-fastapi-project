"""
权限控制模块

处理API权限控制相关的逻辑，检查用户是否有访问指定API的权限。
"""

import re

from fastapi import Depends, Request
from src.common.core.auth.dependency import AuthControl
from src.common.core.constants import RoleCodeConst
from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.storage import TransactionManager
from src.modules.platform.repository.role_subject_repository import (
    role_subject_repository,
)


class PermissionControl:
    """权限控制器

    处理API权限控制相关的逻辑，检查用户是否有访问指定API的权限。
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
            permission_code: 权限编码（可选，用于精确权限校验）
            current_user: 当前认证用户

        Raises:
            HTTPException: 当用户无权限时抛出403错误
        """
        # 通过 role_subject_repository 获取用户角色
        with TransactionManager() as tm:
            auth_ctx = getattr(request.state, "auth_context", None)
            if auth_ctx:
                # 根据主体类型获取角色
                roles = role_subject_repository.get_roles_by_subject(
                    subject_id=auth_ctx.subject_id,
                    subject_type=auth_ctx.subject_type,
                    session=tm.session
                )
            else:
                # 兼容旧逻辑：从用户对象直接获取（如果存在）
                roles = getattr(current_user, 'roles', [])

        # 超级管理员特殊放行：如果用户有平台超级管理员角色，直接允许
        if roles:
            for role in roles:
                if role.code == RoleCodeConst.PLATFORM_SUPER_ADMIN.value:
                    return

        # 如果指定了权限编码，进行精确权限校验
        if permission_code:
            cls._check_permission_code(request, permission_code)
            return

        # 默认的API路径权限校验
        method = request.method
        path = request.url.path

        if not roles:
            raise BusinessException(ResponseCode.FORBIDDEN, "用户未绑定角色")

        all_resources = []
        for role in roles:
            all_resources.extend(getattr(role, 'resources', []))

        for resource in all_resources:
            if getattr(resource, 'api_method', None) == method and getattr(resource, 'api_path', None) is not None:
                pattern = re.sub(r"\{[^}]+\}", r"[^/]+", resource.api_path)
                pattern = f"^{pattern}$"
                if re.match(pattern, path):
                    return

        raise BusinessException(ResponseCode.FORBIDDEN, "无此API访问权限")

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
            raise BusinessException(ResponseCode.FORBIDDEN, "无权限")

        # 权限前缀校验
        if permission_code.startswith("platform:"):
            if auth_ctx.subject_type != 0:
                raise BusinessException(ResponseCode.FORBIDDEN, "无平台权限")
        elif permission_code.startswith("tenant:"):
            if auth_ctx.subject_type != 1:
                raise BusinessException(ResponseCode.FORBIDDEN, "无租户权限")

        # 通过 role_subject_repository 获取用户角色
        with TransactionManager() as tm:
            roles = role_subject_repository.get_roles_by_subject(
                subject_id=auth_ctx.subject_id,
                subject_type=auth_ctx.subject_type,
                session=tm.session
            )

            if not roles:
                raise BusinessException(ResponseCode.FORBIDDEN, "无此权限")

            for role in roles:
                if getattr(role, 'permissions', None):
                    for perm in role.permissions:
                        if getattr(perm, 'code', None) == permission_code:
                            return

        raise BusinessException(ResponseCode.FORBIDDEN, "无此权限")
