"""
租户角色管理接口
"""

from fastapi import APIRouter, Query, Request
from src.common.core.enums.response_code import ResponseCode
from src.common.core.plugins import apply_rate_limit
from src.common.core.response import gen_swagger_response, success, success_page
from src.common.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.modules.tenant.schemas.role import TenantRoleCreate, TenantRoleUpdate

router = APIRouter(
    tags=["租户角色管理"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get("/", summary="获取租户角色列表")
@apply_rate_limit("60/minute")
def list_roles(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    name: str = Query("", description="角色名称"),
):
    """获取当前租户的角色列表"""
    # TODO: 实现租户角色列表查询
    return success_page([], total=0, page=page, page_size=page_size)


@router.get("/{role_id}", summary="获取租户角色详情")
def get_role(request: Request, role_id: int):
    """获取租户角色详情"""
    # TODO: 实现租户角色详情查询
    return success(data={})


@router.post(
    "/",
    summary="创建租户角色",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.DATA_ALREADY_EXIST],
            description="角色名称已存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def create_role(request: Request, role_in: TenantRoleCreate):
    """创建租户角色"""
    # TODO: 实现租户角色创建
    return success(msg="角色创建成功")


@router.put(
    "/{role_id}",
    summary="更新租户角色",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_role(request: Request, role_id: int, role_in: TenantRoleUpdate):
    """更新租户角色"""
    # TODO: 实现租户角色更新
    return success(msg="角色更新成功")


@router.delete(
    "/{role_id}",
    summary="删除租户角色",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_role(request: Request, role_id: int):
    """删除租户角色"""
    # TODO: 实现租户角色删除
    return success(msg="角色删除成功")


@router.put("/{role_id}/permissions", summary="更新租户角色权限")
@apply_rate_limit("30/minute")
def update_role_permissions(
    request: Request,
    role_id: int,
    permission_ids: list[int],
):
    """更新租户角色的权限列表"""
    # TODO: 实现租户角色权限更新
    return success(msg="角色权限更新成功")
