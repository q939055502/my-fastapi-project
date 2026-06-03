from fastapi import APIRouter, Query, Request

from src.core.enums.error_code import ErrorCode
from src.core.handlers import success, success_page
from src.core.handlers.response import gen_swagger_response
from src.core.plugins import apply_rate_limit
from src.core.settings.router_config import DEFAULT_ROUTER_RESPONSES
from src.schemas.sys.resource import ResourceCreate, ResourceUpdate
from src.services.sys.resource_service import resource_service

router = APIRouter(
    tags=["平台管理-资源"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/create",
    summary="创建资源",
    responses={
        400: gen_swagger_response(
            codes=[ErrorCode.DATA_ALREADY_EXIST],
            description="资源名称已存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def create_resource(request: Request, resource_in: ResourceCreate):
    data = resource_service.create_resource(resource_in)
    return success(data=data, msg="资源创建成功")


@router.put(
    "/{resource_id}",
    summary="更新资源",
    responses={
        404: gen_swagger_response(
            codes=[ErrorCode.DATA_NOT_EXIST],
            description="资源不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_resource(request: Request, resource_id: int, resource_in: ResourceUpdate):
    data = resource_service.update_resource(resource_id, resource_in)
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
    "/{resource_id}",
    summary="获取资源详情",
    responses={
        404: gen_swagger_response(
            codes=[ErrorCode.DATA_NOT_EXIST],
            description="资源不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_resource(request: Request, resource_id: int):
    data = resource_service.get_resource_detail(resource_id)
    return success(data=data)


@router.delete(
    "/{resource_id}",
    summary="删除资源",
    responses={
        404: gen_swagger_response(
            codes=[ErrorCode.DATA_NOT_EXIST],
            description="资源不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_resource(request: Request, resource_id: int):
    resource_service.delete_resource(resource_id)
    return success(msg="资源删除成功")
