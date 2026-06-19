from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Query, Request
from pydantic import BaseModel, Field

from src.core.plugins import apply_rate_limit
from src.core.response import ApiResponse, gen_swagger_response
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.foundation.system.schemas.user import UserCreate, UserResponse, UserUpdate
from src.foundation.system.service.user_admin_service import user_admin_service

router = APIRouter(
    tags=["平台管理-用户"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


class ResetPasswordResponse(BaseModel):
    """重置密码响应"""
    password: str = Field(..., description="新密码")


class UserListResponse(BaseModel):
    """用户列表响应(包含分页信息)"""
    list: Annotated[list[UserResponse], Field(..., description="用户列表")]
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")


@router.post(
    "/",
    summary="创建用户",
    responses={
        400: gen_swagger_response(
            codes=[40900],
            description="用户名或邮箱已存在",
        ),
    },
)
@apply_rate_limit("30/minute")
def create_user(request: Request, user_in: UserCreate) -> ApiResponse[UserResponse]:
    user = user_admin_service.create_user(user_in)
    user_response = UserResponse.model_validate(user)
    return ApiResponse(
        code=20000,
        msg="用户创建成功",
        data=user_response
    )


@router.put(
    "/{user_uuid}",
    summary="更新用户",
)
@apply_rate_limit("30/minute")
def update_user(request: Request, user_uuid: UUID, user_in: UserUpdate) -> ApiResponse[None]:
    user_admin_service.update_user(str(user_uuid), user_in)
    return ApiResponse(code=20000, msg="用户更新成功")


@router.put(
    "/reset_password",
    summary="重置密码",
)
@apply_rate_limit("10/minute")
def reset_password(request: Request, user_uuid: UUID = Body(..., description="用户UUID", embed=True)) -> ApiResponse[ResetPasswordResponse]:
    new_password = user_admin_service.reset_user_password(str(user_uuid))
    return ApiResponse(
        code=20000,
        msg="密码重置成功",
        data=ResetPasswordResponse(password=new_password)
    )


@router.get("/list", summary="获取用户列表")
@apply_rate_limit("60/minute")
def list_user(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    username: str = Query("", description="用户名称,用于搜索"),
    email: str = Query("", description="邮箱地址"),
    org_uuid: UUID = Query(None, description="组织UUID"),
) -> ApiResponse[UserListResponse]:
    total, users = user_admin_service.get_user_list(
        page=page,
        page_size=page_size,
        username=username,
        email=email,
        org_uuid=str(org_uuid) if org_uuid else None,
    )
    user_responses = [UserResponse.model_validate(user) for user in users]
    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return ApiResponse(
        code=20000,
        msg="操作成功",
        data=UserListResponse(
            list=user_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    )


@router.get(
    "/{user_uuid}",
    summary="获取用户详情",
    responses={
        404: gen_swagger_response(
            codes=[40401],
            description="用户不存在",
        ),
    },
)
@apply_rate_limit("60/minute")
def get_user(request: Request, user_uuid: UUID) -> ApiResponse[UserResponse]:
    user = user_admin_service.get_user_detail(str(user_uuid))
    user_response = UserResponse.model_validate(user)
    return ApiResponse(code=20000, msg="操作成功", data=user_response)


@router.delete(
    "/{user_uuid}",
    summary="删除用户",
    responses={
        404: gen_swagger_response(
            codes=[40401],
            description="用户不存在",
        ),
    },
)
@apply_rate_limit("30/minute")
def delete_user(request: Request, user_uuid: UUID) -> ApiResponse[None]:
    user_admin_service.delete_user(str(user_uuid))
    return ApiResponse(code=20000, msg="用户删除成功")
