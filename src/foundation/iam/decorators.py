"""
鉴权依赖工厂

提供统一的鉴权依赖函数，用于 FastAPI dependencies 参数：
- require_auth            → 登录认证（单独使用时）
- require_permission      → 操作权限校验（自动包含登录认证）

使用示例：
    # 需要权限的接口（自动带认证）
    @router.post("/users", dependencies=[require_permission("user:create")])
    def create_user():
        pass

    # 只需要认证，不需要权限检查的接口
    @router.get("/me", dependencies=[require_auth])
    def get_profile():
        pass
"""

from fastapi import Depends, Request

from src.foundation.iam.auth.dependency import AuthControl
from src.foundation.iam.rbac.dependency import PermissionControl


require_auth = Depends(AuthControl.is_authed)
"""登录认证依赖

可直接用于 FastAPI dependencies 参数，适用于只需要登录认证、不需要权限检查的接口，如：
    dependencies=[require_auth]
"""


def require_permission(permission_code: str):
    """操作权限依赖工厂

    根据权限编码生成对应的权限校验依赖，**自动包含登录认证**。

    Args:
        permission_code: 权限编码，格式 "资源:动作"，如 "user:create"

    Returns:
        Depends: 权限依赖，可直接用于 FastAPI dependencies
    """
    def permission_check(
        request: Request,
        current_user = Depends(AuthControl.is_authed),
    ):
        PermissionControl._check_permission_code(request, permission_code)

    return Depends(permission_check)
