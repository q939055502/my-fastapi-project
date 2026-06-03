import logging

from fastapi import APIRouter, Query, Request

from src.core.enums.response_code import ResponseCode
from src.core.handlers import success, success_page
from src.core.handlers.response import gen_swagger_response
from src.core.plugins import apply_rate_limit
from src.core.settings.router_config import DEFAULT_ROUTER_RESPONSES
from src.schemas.sys.roles import RoleCreate, RoleUpdate
from src.services.sys.role_service import role_service

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
    "/{role_id}",
    summary="更新角色/职位",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_role(request: Request, role_id: int, role_in: RoleUpdate):
    role_service.update_role(role_id, role_in)
    return success(msg="角色/职位更新成功")


@router.put(
    "/{role_id}/authorized",
    summary="更新角色/职位权限",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_role_authorized(request: Request, role_id: int, role_in: RoleUpdate):
    role_service.update_role_resources(role_id, role_in.resource_ids)
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
    "/{role_id}",
    summary="获取角色/职位详情",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_role(request: Request, role_id: int):
    data = role_service.get_role_detail(role_id)
    return success(data=data)


@router.get(
    "/{role_id}/authorized",
    summary="获取角色/职位权限",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_role_authorized(request: Request, role_id: int):
    data = role_service.get_role_detail(role_id)
    return success(data=data)


@router.delete(
    "/{role_id}",
    summary="删除角色/职位",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="角色不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_role(request: Request, role_id: int):
    role_service.delete_role(role_id)
    return success(msg="角色/职位删除成功")
