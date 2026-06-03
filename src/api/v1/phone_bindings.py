from fastapi import APIRouter, Depends

from src.core.auth import AuthControl, get_current_user_id
from src.core.enums.error_code import ErrorCode
from src.core.handlers import success
from src.core.handlers.response import gen_swagger_response
from src.core.settings.router_config import DEFAULT_ROUTER_RESPONSES
from src.models.iam import User
from src.services.sys.phone_binding_service import phone_binding_service

router = APIRouter(
    prefix="/users/phone-bindings",
    tags=["手机号绑定"],
    responses=DEFAULT_ROUTER_RESPONSES,
)


@router.get(
    "/",
    summary="获取当前用户的手机号绑定列表",
)
def get_my_bindings(
    current_user: User = Depends(AuthControl.is_authed)
):
    user_id = get_current_user_id()
    bindings = phone_binding_service.get_user_bindings(user_id)
    return success(data=bindings)


@router.post(
    "/",
    summary="绑定手机号",
    responses={
        400: gen_swagger_response(
            codes=[ErrorCode.DATA_ALREADY_EXIST],
            description="手机号已被绑定"
        ),
    },
)
def bind_phone(
    phone: str,
    is_primary: bool = True,
    current_user: User = Depends(AuthControl.is_authed)
):
    user_id = get_current_user_id()
    result = phone_binding_service.bind_phone(phone, user_id, is_primary)
    return success(data=result, msg="绑定成功")


@router.delete(
    "/{binding_id}",
    summary="解绑手机号",
    responses={
        404: gen_swagger_response(
            codes=[ErrorCode.DATA_NOT_EXIST],
            description="绑定记录不存在"
        ),
    },
)
def unbind_phone(
    binding_id: int,
    current_user: User = Depends(AuthControl.is_authed)
):
    user_id = get_current_user_id()
    phone_binding_service.unbind_phone(binding_id, user_id)
    return success(msg="解绑成功")
