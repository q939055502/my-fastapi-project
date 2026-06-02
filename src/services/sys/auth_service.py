from typing import Any

from fastapi.exceptions import HTTPException

from src.core.auth import create_token_pair, token_manager, verify_token
from src.core.config import settings
from src.core.constants import (
    HTTP_UNAUTHORIZED,
)
from src.core.log import logger
from src.core.storage import TransactionManager
from src.repositories.sys.user_repository import user_repository
from src.schemas.sys.login import CredentialsSchema, RefreshTokenRequest


class AuthService:
    def __init__(self):
        self.logger = logger

    def login(self, credentials: CredentialsSchema) -> dict[str, Any]:
        self.logger.info(f"用户登录尝试: username={credentials.username}")

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

        self.logger.info(f"用户登录成功: username={credentials.username}, user_id={user.id}")

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
            raise HTTPException(status_code=HTTP_UNAUTHORIZED, detail="无效的Token")

        payload = verify_token(refresh_request.refresh_token, token_type="refresh")
        user_id = payload["user_id"]

        with TransactionManager() as tm:
            user = user_repository.get(id=user_id, session=tm.session)
            if not user or not user.is_active:
                raise HTTPException(status_code=HTTP_UNAUTHORIZED, detail="用户不存在或已被禁用")

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

        self.logger.info(f"Token刷新成功: user_id={user_id}")

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

        self.logger.info("用户登出成功")

    def logout_all(self, user_id: int) -> int:
        count = token_manager.revoke_user_all_tokens(user_id)
        self.logger.info(f"用户从所有设备登出: user_id={user_id}, revoked_tokens={count}")
        return count


auth_service = AuthService()
