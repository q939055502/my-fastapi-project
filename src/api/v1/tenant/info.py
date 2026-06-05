"""
租户成员视角的租户管理接口
"""

from fastapi import APIRouter

from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES

router = APIRouter(
    tags=["租户管理"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get("/", summary="获取当前租户信息")
def get_tenant_info():
    """获取当前登录用户所属租户的信息"""
    pass


@router.put("/settings", summary="更新租户设置")
def update_tenant_settings():
    """更新租户的配置设置"""
    pass
