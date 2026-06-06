from fastapi import APIRouter, Query, Request
from src.common.core.enums.response_code import ResponseCode
from src.common.core.plugins import apply_rate_limit
from src.common.core.response import gen_swagger_response, success
from src.common.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.modules.platform.schemas.dept import DeptCreate, DeptUpdate
from src.modules.platform.service.dept_service import dept_service

router = APIRouter(
    tags=["平台管理-部门"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/",
    summary="创建部门",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.DATA_ALREADY_EXIST],
            description="部门名称已存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def create_dept(request: Request, dept_in: DeptCreate):
    dept_service.create_dept(dept_in)
    return success(msg="部门创建成功")


@router.put(
    "/{dept_id}",
    summary="更新部门",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="部门不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_dept(request: Request, dept_id: int, dept_in: DeptUpdate):
    dept_service.update_dept(dept_id, dept_in)
    return success(msg="部门更新成功")


@router.get("/list", summary="获取部门列表")
@apply_rate_limit("60/minute")
def list_dept(request: Request, name: str = Query(None, description="部门名称")):
    dept_tree = dept_service.get_dept_tree(name or "")
    return success(data=dept_tree)


@router.get(
    "/{dept_id}",
    summary="获取部门详情",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="部门不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_dept(request: Request, dept_id: int):
    data = dept_service.get_dept_detail(dept_id)
    return success(data=data)


@router.delete(
    "/{dept_id}",
    summary="删除部门",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="部门不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_dept(request: Request, dept_id: int):
    dept_service.delete_dept(dept_id)
    return success(msg="部门删除成功")
