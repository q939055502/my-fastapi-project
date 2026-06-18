from uuid import UUID

from fastapi import APIRouter, Query, Request
from src.core.enums.response_code import ResponseCode
from src.core.plugins import apply_rate_limit
from src.core.response import gen_swagger_response, success
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.system.schemas.org import OrgCreate, OrgUpdate
from src.foundation.system.service.org_service import org_service

router = APIRouter(
    tags=["平台管理-组织"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/",
    summary="创建组织",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.DATA_ALREADY_EXIST],
            description="组织名称已存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def create_org(request: Request, org_in: OrgCreate):
    org_service.create_org(org_in)
    return success(msg="组织创建成功")


@router.put(
    "/{org_uuid}",
    summary="更新组织",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="组织不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_org(request: Request, org_uuid: UUID, org_in: OrgUpdate):
    org_service.update_org(org_uuid, org_in)
    return success(msg="组织更新成功")


@router.get("/list", summary="获取组织列表")
@apply_rate_limit("60/minute")
def list_org(request: Request, name: str = Query(None, description="组织名称")):
    org_tree = org_service.get_org_tree(name or "")
    return success(data=org_tree)


@router.get(
    "/{org_uuid}",
    summary="获取组织详情",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="组织不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_org(request: Request, org_uuid: UUID):
    data = org_service.get_org_detail(org_uuid)
    return success(data=data)


@router.delete(
    "/{org_uuid}",
    summary="删除组织",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="组织不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_org(request: Request, org_uuid: UUID):
    org_service.delete_org(org_uuid)
    return success(msg="组织删除成功")