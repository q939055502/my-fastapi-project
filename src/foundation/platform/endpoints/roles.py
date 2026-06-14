import logging
from uuid import UUID

from fastapi import APIRouter, Query, Request
from src.common.core.enums.response_code import ResponseCode
from src.common.core.plugins import apply_rate_limit
from src.common.core.response import gen_swagger_response, success, success_page
from src.common.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.platform.schemas.role import RoleCreate, RoleUpdate
from src.foundation.platform.service.role_service import role_service

logger = logging.getLogger(__name__)
router = APIRouter(
    tags=["平台管理-角色/职位"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/",
    summary="创建角色/职位",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.DATA_ALREADY_EXIST],
            description="角色名称已存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def create_role(request: Request, role_in: RoleCreate):
    role_service.create_role(role_in)
    return success(msg="角色/职位创建成功")


@router.put(
    "/{role_uuid}",
    summary="更新角色/职位",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_role(request: Request, role_uuid: UUID, role_in: RoleUpdate):
    role_service.update_role(role_uuid, role_in)
    return success(msg="角色/职位更新成功")


@router.put(
    "/{role_uuid}/permissions",
    summary="更新角色/职位权限",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_role_permissions(request: Request, role_uuid: UUID, role_in: RoleUpdate):
    role_service.update_role_permissions(role_uuid, role_in.permission_uuids or [])
    return success(msg="权限更新成功")


@router.get("/list", summary="获取角色/职位列表")
@apply_rate_limit("60/minute")
def list_role(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    role_name: str = Query("", description="角色/职位名称，用于查询"),
):
    total, data = role_service.get_role_list(
        page=page,
        page_size=page_size,
        name=role_name
    )
    return success_page(data=data, total=total, page=page, page_size=page_size)


@router.get(
    "/{role_uuid}",
    summary="获取角色/职位详情",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_role(request: Request, role_uuid: UUID):
    data = role_service.get_role_detail(role_uuid)
    return success(data=data)


@router.get(
    "/{role_uuid}/permissions",
    summary="获取角色/职位权限",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_role_permissions(request: Request, role_uuid: UUID):
    data = role_service.get_role_detail(role_uuid)
    return success(data=data)


@router.delete(
    "/{role_uuid}",
    summary="删除角色/职位",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_role(request: Request, role_uuid: UUID):
    role_service.delete_role(role_uuid)
    return success(msg="角色/职位删除成功")