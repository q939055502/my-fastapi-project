from uuid import UUID

from fastapi import APIRouter, Query, Request

from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse, gen_swagger_response
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.system.schemas.org import (
    OrgCreate,
    OrgResponse,
    OrgUpdate,
)
from src.foundation.system.service.org_service import org_service

router = APIRouter(
    tags=["平台管理-组织"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/",
    summary="创建组织",
)
@apply_rate_limit("30/minute")
def create_org(request: Request, org_in: OrgCreate) -> ApiResponse[OrgResponse]:
    org = org_service.create_org(org_in)
    org_response = OrgResponse.model_validate(org)
    return ApiResponse(code=20000, msg="组织创建成功", data=org_response)


@router.put(
    "/{org_uuid}",
    summary="更新组织",
    responses={
        404: gen_swagger_response(
            codes=[40401],
            description="组织不存在",
        ),
    },
)
@apply_rate_limit("30/minute")
def update_org(request: Request, org_uuid: UUID, org_in: OrgUpdate) -> ApiResponse[None]:
    org_service.update_org(str(org_uuid), org_in)
    return ApiResponse(code=20000, msg="组织更新成功")


@router.get("/list", summary="获取组织列表")
@apply_rate_limit("60/minute")
def list_org(request: Request, name: str = Query(None, description="组织名称")) -> ApiResponse[list[OrgResponse]]:
    org_tree = org_service.get_org_tree(name or "")
    org_responses = [OrgResponse.model_validate(org) for org in org_tree]
    return ApiResponse(code=20000, msg="操作成功", data=org_responses)


@router.get(
    "/{org_uuid}",
    summary="获取组织详情",
    responses={
        404: gen_swagger_response(
            codes=[40401],
            description="组织不存在",
        ),
    },
)
@apply_rate_limit("60/minute")
def get_org(request: Request, org_uuid: UUID) -> ApiResponse[OrgResponse]:
    org = org_service.get_org_detail(str(org_uuid))
    org_response = OrgResponse.model_validate(org)
    return ApiResponse(code=20000, msg="操作成功", data=org_response)


@router.delete(
    "/{org_uuid}",
    summary="删除组织",
)
@apply_rate_limit("30/minute")
def delete_org(request: Request, org_uuid: UUID) -> ApiResponse[None]:
    org_service.delete_org(str(org_uuid))
    return ApiResponse(code=20000, msg="组织删除成功")
