"""
鉴权依赖工厂

提供统一的鉴权依赖函数，用于 FastAPI dependencies 参数:
- require_auth            -> 登录认证（单独使用时）
- require_permission      -> 操作权限校验（自动包含登录认证）

依赖来源:
- 认证逻辑: src.foundation.iam.auth.auth_control.AuthControl.authenticate_token
- 权限逻辑: src.foundation.iam.rbac.permission_control.PermissionControl.check_permission_code

使用示例：
    # 需要权限的接口（自动带认证）
    @router.post("/users", dependencies=[require_permission("platform:user:create")])
    def create_user(): ...

    # 只需要认证，不需要权限检查的接口
    @router.get("/me", dependencies=[require_auth])
    def get_profile(): ...
"""

from fastapi import Depends, Request
from fastapi.security import HTTPBearer

from src.foundation.iam.auth.auth_control import AuthControl
from src.foundation.iam.rbac.permission_control import PermissionControl

bearer_scheme = HTTPBearer()

REGISTERED_PERMISSIONS = set()


def _auth_dep(token=Depends(bearer_scheme)):
    """登录认证依赖内部实现

    从 Authorization: Bearer <token> 取 access token，
    调 AuthControl.authenticate_token 验证并返回 User 对象。
    """
    return AuthControl.authenticate_token(token.credentials)


require_auth = Depends(_auth_dep)
"""登录认证依赖

可直接用于 FastAPI dependencies 参数，适用于只需要登录认证、不需要权限检查的接口。
"""


def require_permission(permission_code: str):
    """操作权限依赖工厂

    根据权限编码生成对应的权限校验依赖，**自动包含登录认证**。

    Args:
        permission_code: 权限编码，格式 "适用范围:资源:动作"，如 "platform:user:create", "all:order:delete"

    Returns:
        Depends: 权限依赖，可直接用于 FastAPI dependencies
    """
    REGISTERED_PERMISSIONS.add(permission_code)

    def permission_check(
        request: Request,
        current_user=Depends(_auth_dep),
    ):
        PermissionControl.check_permission_code(request, permission_code)

    return Depends(permission_check)