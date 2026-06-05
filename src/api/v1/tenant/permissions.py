"""
租户权限管理接口
"""

from fastapi import APIRouter, Query, Request

from src.core.handlers import success, success_page
from src.core.plugins import apply_rate_limit
from src.core.settings.router_config import DEFAULT_ROUTER_RESPONSES

router = APIRouter(
    tags=["租户权限管理"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get("/", summary="获取租户权限列表")
@apply_rate_limit("60/minute")
def list_permissions(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取当前租户的权限列表"""
    # TODO: 实现租户权限列表查询
    return success_page([], total=0, page=page, page_size=page_size)


@router.get("/tree", summary="获取租户权限树")
@apply_rate_limit("60/minute")
def get_permission_tree(request: Request):
    """获取当前租户的权限树形结构"""
    # TODO: 实现租户权限树查询
    return success(data=[])
