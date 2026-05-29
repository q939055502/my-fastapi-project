from typing import Any

from fastapi.exceptions import HTTPException

from src.core.constants import (
    HTTP_BAD_REQUEST,
    HTTP_FORBIDDEN,
    HTTP_NOT_FOUND,
)
from src.core.log import logger
from src.core.storage import UnitOfWork
from src.repositories.sys.phone_binding_repository import phone_binding_repository
from src.repositories.sys.user_repository import user_repository


class PhoneBindingService:
    def __init__(self):
        self.logger = logger

    def bind_phone(self, phone: str, user_id: int, is_primary: bool = True) -> dict[str, Any]:
        """绑定手机号

        Args:
            phone: 手机号码
            user_id: 用户ID
            is_primary: 是否为主绑定（自有账号）

        Returns:
            绑定记录信息
        """
        self.logger.info(f"绑定手机号: phone={phone}, user_id={user_id}, is_primary={is_primary}")

        with UnitOfWork() as uow:
            user = user_repository.get(id=user_id, session=uow.session)
            if not user:
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="用户不存在")

            if is_primary:
                existing_primary = phone_binding_repository.get_primary_binding(phone, uow.session)
                if existing_primary:
                    raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="该手机号已绑定自有账号")
            else:
                existing_bindings = phone_binding_repository.get_by_phone(phone, uow.session)
                for binding in existing_bindings:
                    if binding.user_id == user_id:
                        raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="该手机号已绑定")

            binding = phone_binding_repository.create_binding(
                phone=phone,
                user_id=user_id,
                is_primary=is_primary,
                session=uow.session
            )

            uow.commit()

            self.logger.info(f"手机号绑定成功: phone={phone}, user_id={user_id}")

            return {
                "id": binding.id,
                "phone": binding.phone,
                "user_id": binding.user_id,
                "is_primary": binding.is_primary,
                "created_at": binding.created_at
            }

    def unbind_phone(self, binding_id: int, user_id: int) -> None:
        """解绑手机号"""
        self.logger.info(f"解绑手机号: binding_id={binding_id}, user_id={user_id}")

        with UnitOfWork() as uow:
            binding = phone_binding_repository.get(id=binding_id, session=uow.session)
            if not binding:
                raise HTTPException(status_code=HTTP_NOT_FOUND, detail="绑定记录不存在")

            if binding.user_id != user_id:
                raise HTTPException(status_code=HTTP_FORBIDDEN, detail="无权解绑此手机号")

            if binding.is_primary:
                raise HTTPException(status_code=HTTP_BAD_REQUEST, detail="主绑定账号不允许解绑")

            phone_binding_repository.delete(id=binding_id, session=uow.session)
            uow.commit()

            self.logger.info(f"手机号解绑成功: binding_id={binding_id}")

    def get_user_bindings(self, user_id: int) -> list[dict[str, Any]]:
        """获取用户的所有手机号绑定记录"""
        with UnitOfWork() as uow:
            bindings = phone_binding_repository.get_by_user_id(user_id, uow.session)

            result = []
            for binding in bindings:
                result.append({
                    "id": binding.id,
                    "phone": binding.phone,
                    "is_primary": binding.is_primary,
                    "created_at": binding.created_at
                })

            return result

    def get_phone_bindings(self, phone: str) -> dict[str, Any]:
        """获取手机号的所有绑定记录"""
        with UnitOfWork() as uow:
            primary = phone_binding_repository.get_primary_binding(phone, uow.session)
            secondary = phone_binding_repository.get_secondary_bindings(phone, uow.session)

            result = {
                "phone": phone,
                "primary": None,
                "secondary": []
            }

            if primary:
                result["primary"] = {
                    "id": primary.id,
                    "user_id": primary.user_id,
                    "created_at": primary.created_at
                }

            for binding in secondary:
                result["secondary"].append({
                    "id": binding.id,
                    "user_id": binding.user_id,
                    "created_at": binding.created_at
                })

            return result


phone_binding_service = PhoneBindingService()
