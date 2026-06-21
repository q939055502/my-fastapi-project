"""
权限控制模块

处理API权限控制相关的逻辑,检查用户是否有访问指定API的权限。

RBAC 模型:
- 一个用户可能同时有两层身份: 平台用户 (subject_type=0) + 租户成员 (subject_type=1)
- 权限校验时两层身份都查, 权限码取并集
- 角色缓存(rbac:role)  -> f"{subject_type}:{subject_id}" -> 角色ID列表
- 权限缓存(rbac:perm)   -> f"{subject_type}:{subject_id}" -> 权限编码集合

subject_type 取值:
  0 = 平台用户, subject_id = user_id
  1 = 租户成员, subject_id = member.subject_id (member 表唯一)

读流程(鉴权):
  权限缓存命中 -> 直接匹配
  权限缓存未命中 -> 角色缓存
    角色缓存未命中 -> 查数据库拿角色 -> 写角色缓存
  用角色查权限 -> 写权限缓存
  平台身份权限码 + 租户身份权限码 -> 并集去重

缓存失效(供角色/权限管理模块调用):
  角色绑定/解绑 -> invalidate_rbac_cache(subject_type, subject_id)
  角色权限变更(增/删权限) -> invalidate_all_rbac_cache()
"""

from fastapi import Request

from src.core.constants import RoleCodeConst
from src.core.exceptions import BusinessException
from src.core.storage import TransactionManager, cache_manager
from src.foundation.iam.auth.context import get_current_auth_context
from src.foundation.iam.rbac.repository.permission_repository import (
    permission_repository,
)
from src.foundation.iam.rbac.repository.role_repository import role_repository
from src.foundation.iam.rbac.repository.role_subject_repository import (
    role_subject_repository,
)


RBAC_ROLE_RESOURCE = "rbac:role"
RBAC_PERM_RESOURCE = "rbac:perm"

PLATFORM_SUBJECT_TYPE = 0
TENANT_SUBJECT_TYPE = 1


class PermissionControl:
    """权限控制类

    处理API权限控制相关的逻辑,检查用户是否有访问指定API的权限。
    同时查平台身份 + 租户身份, 权限码并集。
    """

    @classmethod
    def _get_cached_permission_codes(cls, subject_type: int, subject_id: int) -> list[str] | None:
        """从缓存获取权限编码列表"""
        cache_key = f"{subject_type}:{subject_id}"
        return cache_manager.get_global(RBAC_PERM_RESOURCE, cache_key)

    @classmethod
    def _get_cached_role_ids(cls, subject_type: int, subject_id: int) -> list[int] | None:
        """从缓存获取角色ID列表"""
        cache_key = f"{subject_type}:{subject_id}"
        return cache_manager.get_global(RBAC_ROLE_RESOURCE, cache_key)

    @classmethod
    def _set_role_cache(cls, subject_type: int, subject_id: int, role_ids: list[int]) -> None:
        """写角色缓存(包含空列表,用于防御性缓存)"""
        cache_key = f"{subject_type}:{subject_id}"
        cache_manager.set_global(RBAC_ROLE_RESOURCE, cache_key, role_ids)

    @classmethod
    def _set_perm_cache(cls, subject_type: int, subject_id: int, perm_codes: list[str]) -> None:
        """写权限缓存(包含空列表,防御无权限用户攻击)"""
        cache_key = f"{subject_type}:{subject_id}"
        cache_manager.set_global(RBAC_PERM_RESOURCE, cache_key, perm_codes)

    @classmethod
    def _load_permission_codes(cls, subject_type: int, subject_id: int, session) -> list[str]:
        """从数据库加载指定主体的所有权限编码"""
        role_ids = role_subject_repository.get_role_ids_by_subject(
            subject_id=subject_id,
            subject_type=subject_type,
            session=session,
        )

        cls._set_role_cache(subject_type, subject_id, role_ids)

        if not role_ids:
            return []

        roles = role_repository.list_by_ids(role_ids=role_ids, session=session)

        permission_codes: list[str] = []
        for role in roles:
            if role.code == RoleCodeConst.PLATFORM_SUPER_ADMIN.value:
                return ["__SUPER_ADMIN__"]

            perms = permission_repository.get_permissions_by_role(role.id, session)
            for perm in perms:
                permission_codes.append(perm.permission_code)

        return permission_codes

    @classmethod
    def _get_permission_codes(cls, subject_type: int, subject_id: int, session) -> list[str]:
        """获取权限编码列表(走缓存,未命中查数据库)"""
        cached = cls._get_cached_permission_codes(subject_type, subject_id)
        if cached is not None:
            return cached

        perm_codes = cls._load_permission_codes(subject_type, subject_id, session)
        cls._set_perm_cache(subject_type, subject_id, perm_codes)
        return perm_codes

    @classmethod
    def check_permission_code(cls, request: Request, permission_code: str) -> None:
        """检查指定的权限编码

        同时查平台身份 + 租户身份, 权限码并集去重。

        Raises:
            HTTPException: 当用户无权限时抛出403错误
        """
        auth_ctx = get_current_auth_context()

        if not auth_ctx:
            raise BusinessException(40300, "无权限")

        all_perm_codes: set[str] = set()
        super_admin = False

        with TransactionManager() as tm:
            if auth_ctx.user_id:
                codes = cls._get_permission_codes(
                    PLATFORM_SUBJECT_TYPE, auth_ctx.user_id, tm.session)
                all_perm_codes.update(codes)
                if "__SUPER_ADMIN__" in codes:
                    super_admin = True

            if auth_ctx.member_id:
                codes = cls._get_permission_codes(
                    TENANT_SUBJECT_TYPE, auth_ctx.member_id, tm.session)
                all_perm_codes.update(codes)
                if "__SUPER_ADMIN__" in codes:
                    super_admin = True

        if super_admin or permission_code in all_perm_codes:
            return

        raise BusinessException(40300, "无此权限")


def invalidate_rbac_cache(subject_type: int, subject_id: int) -> None:
    """清除指定主体的 RBAC 缓存

    角色绑定/解绑时调用。
    """
    cache_key = f"{subject_type}:{subject_id}"
    cache_manager.delete_global(RBAC_ROLE_RESOURCE, cache_key)
    cache_manager.delete_global(RBAC_PERM_RESOURCE, cache_key)


def invalidate_all_rbac_cache() -> None:
    """清除所有 RBAC 缓存

    角色权限变更(增/删权限)时调用。
    由于角色权限变更影响所有拥有该角色的用户,全量清除最简单安全。
    """
    cache_manager._clear_pattern_raw(f"{RBAC_ROLE_RESOURCE}:*")
    cache_manager._clear_pattern_raw(f"{RBAC_PERM_RESOURCE}:*")
