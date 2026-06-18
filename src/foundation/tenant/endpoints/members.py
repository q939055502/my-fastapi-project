"""
租户成员管理接口
"""

from uuid import UUID

from fastapi import APIRouter
from src.core.response.router_config import DEFAULT_ROUTER_RESPONSES

router = APIRouter(
    tags=["租户成员"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get("/", summary="获取租户成员列表")
def list_members():
    """获取当前租户的成员列表"""
    pass


@router.post("/", summary="邀请成员加入租户")
def invite_member():
    """邀请用户加入当前租户"""
    pass


@router.delete("/{member_uuid}", summary="移除租户成员")
def remove_member(member_uuid: UUID):
    """从租户中移除指定成员"""
    pass