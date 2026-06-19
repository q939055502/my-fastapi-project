"""
Account bind management endpoints
"""
from uuid import UUID

from fastapi import APIRouter, Depends

from src.core.response import ApiResponse
from src.foundation.iam import AuthControl
from src.foundation.system.schemas.account_bind import (
    AccountBindCreate,
    AccountBindResponse,
)
from src.foundation.system.service.account_bind_service import account_bind_service
from src.models.platform import User

router = APIRouter(
    prefix="/binds",
    tags=["Account Bind"],
)


@router.get("/", summary="Get user's bind list")
def get_my_bindings(current_user: User = Depends(AuthControl.is_authed)) -> ApiResponse[list[AccountBindResponse]]:
    bindings = account_bind_service.get_user_bindings(current_user.uuid)
    binding_responses = [AccountBindResponse.model_validate(bind) for bind in bindings]
    return ApiResponse(code=20000, data=binding_responses)


@router.post("/", summary="Bind phone/email")
def bind_value(
    bind_data: AccountBindCreate,
    current_user: User = Depends(AuthControl.is_authed),
) -> ApiResponse[AccountBindResponse]:
    bind = account_bind_service.create_bind(current_user.uuid, bind_data)
    bind_response = AccountBindResponse.model_validate(bind)
    return ApiResponse(code=20000, data=bind_response, msg="Bind created successfully, please verify")


@router.post("/set_default", summary="Set default bind")
def set_default_bind(
    bind_uuid: UUID,
    current_user: User = Depends(AuthControl.is_authed),
) -> ApiResponse[AccountBindResponse]:
    bind = account_bind_service.set_default_bind(current_user.uuid, bind_uuid)
    bind_response = AccountBindResponse.model_validate(bind)
    return ApiResponse(code=20000, data=bind_response, msg="Set as default successfully")


@router.delete("/{bind_uuid}", summary="Unbind")
def unbind_value(
    bind_uuid: UUID,
    current_user: User = Depends(AuthControl.is_authed),
) -> ApiResponse[None]:
    account_bind_service.delete_bind(current_user.uuid, bind_uuid)
    return ApiResponse(code=20000, msg="Unbind successfully")
