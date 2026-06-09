"""
Account bind management endpoints
"""
from fastapi import APIRouter, Depends
from src.common.core.auth import AuthControl
from src.common.core.response import success
from src.common.core.response.router_config import DEFAULT_ROUTER_RESPONSES
from src.models.platform import User
from src.foundation.system.schemas.account_bind import AccountBindCreate
from src.foundation.system.service.account_bind_service import account_bind_service

router = APIRouter(
    prefix="/binds",
    tags=["Account Bind"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get("/", summary="Get user's bind list")
def get_my_bindings(current_user: User = Depends(AuthControl.is_authed)):
    bindings = account_bind_service.get_user_bindings(current_user.id)
    return success(data=bindings)


@router.post("/", summary="Bind phone/email")
def bind_value(
    bind_data: AccountBindCreate,
    current_user: User = Depends(AuthControl.is_authed),
):
    bind = account_bind_service.create_bind(current_user.id, bind_data)
    return success(data=bind, msg="Bind created successfully, please verify")


@router.post("/set_default", summary="Set default bind")
def set_default_bind(
    bind_id: int,
    current_user: User = Depends(AuthControl.is_authed),
):
    bind = account_bind_service.set_default_bind(current_user.id, bind_id)
    return success(data=bind, msg="Set as default successfully")


@router.delete("/{bind_id}", summary="Unbind")
def unbind_value(
    bind_id: int,
    current_user: User = Depends(AuthControl.is_authed),
):
    account_bind_service.delete_bind(current_user.id, bind_id)
    return success(msg="Unbind successfully")
