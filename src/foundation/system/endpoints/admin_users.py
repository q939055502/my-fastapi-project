from uuid import UUID

from fastapi import APIRouter, Body, Query, Request
from src.core.enums.response_code import ResponseCode
from src.core.plugins import apply_rate_limit
from src.core.response import gen_swagger_response, success, success_page
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.system.schemas.user import UserCreate, UserUpdate
from src.foundation.system.service.user_admin_service import user_admin_service

router = APIRouter(
    tags=["平台管理-用户"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.post(
    "/",
    summary="创建用户",
    responses={
        400: gen_swagger_response(
            codes=[ResponseCode.DATA_ALREADY_EXIST],
            description="用户名或邮箱已存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def create_user(request: Request, user_in: UserCreate):
    user_data = user_admin_service.create_user(user_in)
    return success(data=user_data, msg="用户创建成功")


@router.put(
    "/{user_uuid}",
    summary="更新用户",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="用户不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def update_user(request: Request, user_uuid: UUID, user_in: UserUpdate):
    user_admin_service.update_user(user_uuid, user_in)
    return success(msg="用户更新成功")


@router.put(
    "/reset_password",
    summary="重置密码",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="用户不存在"
        ),
    },
)
@apply_rate_limit("10/minute")
def reset_password(request: Request, user_uuid: UUID = Body(..., description="用户UUID", embed=True)):
    new_password = user_admin_service.reset_user_password(user_uuid)
    return success(data={"password": new_password}, msg="密码重置成功")


@router.get("/list", summary="获取用户列表")
@apply_rate_limit("60/minute")
def list_user(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    username: str = Query("", description="用户名称，用于搜索"),
    email: str = Query("", description="邮箱地址"),
    org_uuid: UUID = Query(None, description="组织UUID"),
):
    total, data = user_admin_service.get_user_list(
        page=page,
        page_size=page_size,
        username=username,
        email=email,
        org_uuid=org_uuid,
    )
    return success_page(data=data, total=total, page=page, page_size=page_size)


@router.get(
    "/{user_uuid}",
    summary="获取用户详情",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="用户不存在"
        ),
    },
)
@apply_rate_limit("60/minute")
def get_user(request: Request, user_uuid: UUID):
    user_data = user_admin_service.get_user_detail(user_uuid)
    return success(data=user_data)


@router.delete(
    "/{user_uuid}",
    summary="删除用户",
    responses={
        404: gen_swagger_response(
            codes=[ResponseCode.DATA_NOT_EXIST],
            description="用户不存在"
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_user(request: Request, user_uuid: UUID):
    user_admin_service.delete_user(user_uuid)
    return success(msg="用户删除成功")