from fastapi import APIRouter, Depends

from src.core.auth import AuthControl
from src.core.handlers import success
from src.core.settings.router_config import DEFAULT_ROUTER_RESPONSES
from src.models.iam import User

router = APIRouter(
    prefix="/users/binds",
    tags=["用户绑定"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get(
    "/",
    summary="获取当前用户的绑定列表",
)
def get_my_bindings(
    current_user: User = Depends(AuthControl.is_authed)
):
    return success(data=[])


@router.post(
    "/",
    summary="绑定手机号/邮箱",
)
def bind_value(
    bind_type: int,
    value: str,
    is_default: bool = False,
    current_user: User = Depends(AuthControl.is_authed)
):
    return success(data={}, msg="绑定成功")


@router.delete(
    "/{binding_id}",
    summary="解绑",
)
def unbind_value(
    binding_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    return success(msg="解绑成功")
