from fastapi import APIRouter, Query, Depends, Request

from src.core.response import success, success_page
from src.core.dependency import AuthControl
from src.core.rate_limit import apply_rate_limit

router = APIRouter()


@router.put("/{tenant_id}", summary="更新租户")
@apply_rate_limit("30/minute")
def update_tenant(
    request: Request,
    tenant_id: int,
    current_user = Depends(AuthControl.is_authed),
):
    return success(msg="租户更新成功")


@router.get("/list", summary="获取租户列表")
@apply_rate_limit("60/minute")
def list_tenants(
    request: Request,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query("", description="租户名称"),
    current_user = Depends(AuthControl.is_authed),
):
    return success_page(data=[], total=0, page=page, page_size=page_size)


@router.get("/{tenant_id}", summary="获取租户详情")
@apply_rate_limit("60/minute")
def get_tenant(
    request: Request,
    tenant_id: int,
    current_user = Depends(AuthControl.is_authed),
):
    return success(data={})
