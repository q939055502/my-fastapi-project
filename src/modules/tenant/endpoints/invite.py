"""
租户邀请/申请管理接口
"""

from fastapi import APIRouter, Query, Request
from src.common.core.plugins import apply_rate_limit
from src.common.core.response import success, success_page
from src.common.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.modules.tenant.schemas.invite import InviteCreate

router = APIRouter(
    tags=["租户邀请管理"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get("/invitations", summary="获取邀请列表")
@apply_rate_limit("60/minute")
def list_invitations(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取租户的邀请记录列表"""
    # TODO: 实现邀请列表查询
    return success_page([], total=0, page=page, page_size=page_size)


@router.get("/applications", summary="获取待审核申请列表")
@apply_rate_limit("60/minute")
def list_applications(
    request: Request,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
):
    """获取待审核的加入申请列表"""
    # TODO: 实现申请列表查询
    return success_page([], total=0, page=page, page_size=page_size)


@router.post("/invite", summary="发送定向邀请")
@apply_rate_limit("10/minute")
def send_invite(request: Request, invite_in: InviteCreate):
    """发送定向邀请（手机号/邮箱）"""
    # TODO: 实现定向邀请
    return success(msg="邀请发送成功")


@router.post("/public-link", summary="生成公开邀请链接")
@apply_rate_limit("10/minute")
def create_public_link(request: Request):
    """生成公开邀请链接"""
    # TODO: 实现公开邀请链接生成
    return success(data={"invite_code": "", "invite_url": ""})


@router.put("/public-link", summary="更新公开邀请设置")
@apply_rate_limit("10/minute")
def update_public_link(request: Request, need_audit: bool = False):
    """更新公开邀请设置（是否需要审批）"""
    # TODO: 实现公开邀请设置更新
    return success(msg="设置更新成功")


@router.post("/applications/{application_id}/approve", summary="通过申请")
@apply_rate_limit("30/minute")
def approve_application(request: Request, application_id: int):
    """通过加入申请"""
    # TODO: 实现申请通过
    return success(msg="申请已通过")


@router.post("/applications/{application_id}/reject", summary="拒绝申请")
@apply_rate_limit("30/minute")
def reject_application(
    request: Request,
    application_id: int,
    reason: str = Query("", description="拒绝原因"),
):
    """拒绝加入申请"""
    # TODO: 实现申请拒绝
    return success(msg="申请已拒绝")


@router.delete("/invitations/{invite_id}", summary="撤销邀请")
@apply_rate_limit("30/minute")
def cancel_invite(request: Request, invite_id: int):
    """撤销邀请"""
    # TODO: 实现邀请撤销
    return success(msg="邀请已撤销")
