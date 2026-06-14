from uuid import UUID

from fastapi import APIRouter, Query, Request
from src.common.core.enums.response_code import ResponseCode
from src.common.core.plugins import apply_rate_limit
from src.common.core.response import gen_swagger_response, success, success_page
from src.common.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.platform.schemas.permission import PermissionCreate, PermissionUpdate
from src.foundation.platform.service.permission_service import resource_service

router = APIRouter(
    tags=["平台管理-资源"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/create",
    summary="创建资源",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.DATA_ALREADY_EXIST],
            description="资源名称已存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def create_resource(request: Request, resource_in: PermissionCreate):
    data = resource_service.create_resource(resource_in)
    return success(data=data, msg="资源创建成功")


@router.put(
    "/{resource_uuid}",
    summary="更新资源",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="资源不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_resource(request: Request, resource_uuid: UUID, resource_in: PermissionUpdate):
    data = resource_service.update_resource(resource_uuid, resource_in)
    return success(data=data, msg="资源更新成功")


@router.get("/list", summary="获取资源列表")
@apply_rate_limit("60/minute")
def list_resource(
    request: Request,
    resource_type: int = Query(None, description="资源类型：1-菜单 2-API 3-按钮"),
    name: str = Query("", description="资源名称"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    total, data = resource_service.get_resource_list(type=resource_type, name=name, page=page, page_size=page_size)
    return success_page(data=data, total=total, page=page, page_size=page_size)


@router.get("/types", summary="获取资源类型")
@apply_rate_limit("60/minute")
def get_resource_types(request: Request):
    data = resource_service.get_resource_types()
    return success(data=data)


@router.get(
    "/{resource_uuid}",
    summary="获取资源详情",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="资源不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_resource(request: Request, resource_uuid: UUID):
    data = resource_service.get_resource_detail(resource_uuid)
    return success(data=data)


@router.delete(
    "/{resource_uuid}",
    summary="删除资源",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="资源不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_resource(request: Request, resource_uuid: UUID):
    resource_service.delete_resource(resource_uuid)
    return success(msg="资源删除成功")