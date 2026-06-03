from typing import Any

from src.core.auth import create_token_pair, token_manager, verify_token
from src.core.config import settings
from src.core.constants import ROLE_PLATFORM_NORMAL_USER
from src.core.enums.response_code import ResponseCode
from src.core.exceptions.exception import BusinessException
from src.core.log import logger
from src.core.storage import TransactionManager
from src.repositories.sys.role_repository import role_repository
from src.repositories.sys.user_repository import user_repository
from src.schemas.sys.login import (
    CredentialsSchema,
    RefreshTokenRequest,
    UserRegisterSchema,
)
from src.schemas.sys.users import UserCreate


class AuthService:
    def register(self, register_in: UserRegisterSchema) -> dict[str, Any]:
        """
        用户自主注册
        """
        logger.info(f"用户注册尝试: username={register_in.username}")

        if not settings.ALLOW_USER_REGISTRATION:
            raise BusinessException(ResponseCode.FORBIDDEN, "用户注册功能已关闭")

        with TransactionManager() as tm:
            existing_user_by_username = user_repository.get_by_username(register_in.username, session=tm.session)
            if existing_user_by_username:
                raise BusinessException(
                    ResponseCode.PARAM_ERROR,
                    detail=f"用户名 '{register_in.username}' 已存在",
                )

            existing_user_by_email = user_repository.get_by_email(register_in.email, session=tm.session)
            if existing_user_by_email:
                raise BusinessException(
                    ResponseCode.PARAM_ERROR,
                    detail=f"邮箱 '{register_in.email}' 已存在",
                )

            user_create = UserCreate(
                username=register_in.username,
                email=register_in.email,
                password=register_in.password,
                role_ids=[],
            )

            new_user = user_repository.create_user(obj_in=user_create, session=tm.session)

            default_role = tm.session.execute(
                role_repository.model.__table__.select()
                .where(role_repository.model.name == ROLE_PLATFORM_NORMAL_USER)
            ).first()
            if default_role:
                user_repository.update_roles(new_user, [default_role.id], session=tm.session)
                logger.info(f"用户 {register_in.username} 自动分配默认角色: {ROLE_PLATFORM_NORMAL_USER}")

            tm.commit()

        result = {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "created_at": new_user.created_at,
        }

        logger.info(f"用户注册成功: username={register_in.username}, user_id={new_user.id}")

        if settings.AUTO_LOGIN_AFTER_REGISTER:
            access_token, refresh_token = create_token_pair(
                user_id=new_user.id, username=new_user.username
            )

            access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

            token_manager.store_access_token(access_token, new_user.id, access_ttl)
            token_manager.store_refresh_token(refresh_token, new_user.id, access_token, refresh_ttl)
            token_manager.add_user_token(new_user.id, access_token, refresh_token, refresh_ttl)

            result["access_token"] = access_token
            result["refresh_token"] = refresh_token
            result["token_type"] = "bearer"
            result["expires_in"] = access_ttl

        return result

    def login(self, credentials: CredentialsSchema) -> dict[str, Any]:
        logger.info(f"用户登录尝试: username={credentials.username}")

        with TransactionManager() as tm:
            user = user_repository.authenticate(credentials, session=tm.session)
            user_repository.update_last_login(user.id, session=tm.session)
            tm.commit()

        access_token, refresh_token = create_token_pair(
            user_id=user.id, username=user.username
        )

        access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        token_manager.store_access_token(access_token, user.id, access_ttl)
        token_manager.store_refresh_token(refresh_token, user.id, access_token, refresh_ttl)
        token_manager.add_user_token(user.id, access_token, refresh_token, refresh_ttl)

        logger.info(f"用户登录成功: username={credentials.username}, user_id={user.id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "username": user.username,
            "token_type": "bearer",
            "expires_in": access_ttl
        }

    def refresh_token(self, refresh_request: RefreshTokenRequest) -> dict[str, Any]:
        refresh_data = token_manager.get_refresh_token_data(refresh_request.refresh_token)
        if not refresh_data:
            raise BusinessException(ResponseCode.UNAUTHORIZED, "无效的Token")

        payload = verify_token(refresh_request.refresh_token, token_type="refresh")
        user_id = payload["user_id"]

        with TransactionManager() as tm:
            user = user_repository.get(id=user_id, session=tm.session)
            if not user or not user.is_active:
                raise BusinessException(ResponseCode.UNAUTHORIZED, "用户不存在或已被禁用")

        old_access_token = refresh_data.get("linked_access")

        if old_access_token:
            token_manager.revoke_access_token(old_access_token)
        token_manager.revoke_refresh_token(refresh_request.refresh_token)

        access_token, new_refresh_token = create_token_pair(
            user_id=user.id, username=user.username
        )

        access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        token_manager.store_access_token(access_token, user.id, access_ttl)
        token_manager.store_refresh_token(new_refresh_token, user.id, access_token, refresh_ttl)
        token_manager.add_user_token(user.id, access_token, new_refresh_token, refresh_ttl)

        logger.info(f"Token刷新成功: user_id={user_id}")

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": access_ttl
        }

    def logout(self, access_token: str, refresh_token: str = None) -> None:
        token_manager.revoke_access_token(access_token)

        if refresh_token:
            token_manager.revoke_refresh_token(refresh_token)
            user_id = token_manager.get_user_id_by_access_token(access_token)
            if user_id:
                token_manager.remove_token_from_user_set(user_id, access_token, refresh_token)

        logger.info("用户登出成功")

    def logout_all(self, user_id: int) -> int:
        count = token_manager.revoke_user_all_tokens(user_id)
        logger.info(f"用户从所有设备登出: user_id={user_id}, revoked_tokens={count}")
        return count


auth_service = AuthService()
