from fastapi import APIRouter, Depends

from src.core.auth import AuthControl, get_current_user_id
from src.core.handlers import success
from src.models.iam import User
from src.services.sys.phone_binding_service import phone_binding_service

router = APIRouter(prefix="/users/phone-bindings", tags=["手机号绑定"])


@router.get("/", summary="获取当前用户的手机号绑定列表")
def get_my_bindings(
    current_user: User = Depends(AuthControl.is_authed)
):
    user_id = get_current_user_id()
    bindings = phone_binding_service.get_user_bindings(user_id)
    return success(data=bindings)


@router.post("/", summary="绑定手机号")
def bind_phone(
    phone: str,
    is_primary: bool = True,
    current_user: User = Depends(AuthControl.is_authed)
):
    user_id = get_current_user_id()
    result = phone_binding_service.bind_phone(phone, user_id, is_primary)
    return success(data=result, msg="绑定成功")


@router.delete("/{binding_id}", summary="解绑手机号")
def unbind_phone(
    binding_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    user_id = get_current_user_id()
    phone_binding_service.unbind_phone(binding_id, user_id)
    return success(msg="解绑成功")
