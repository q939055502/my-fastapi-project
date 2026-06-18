import re
from typing import Any, List, Tuple
from uuid import UUID

from sqlalchemy import select
from src.foundation.iam.auth import create_token_pair, token_manager, verify_token
from src.core.config import settings
from src.core.constants import RoleCodeConst
from src.core.enums.response_code import ResponseCode
from src.core.exceptions import BusinessException
from src.core.log import logger
from src.core.storage import TransactionManager
from src.foundation.iam.auth.repository.auth_repository import auth_repository
from src.foundation.iam.auth.schemas.login import LoginByPasswordStep1Request
from src.foundation.iam.auth.schemas.register import UserRegisterSchema
from src.foundation.iam.auth.schemas.token import RefreshTokenRequest
from src.foundation.iam.rbac.repository.role_repository import role_repository
from src.foundation.system.repository.user_repository import user_repository
from src.foundation.system.schemas.user import UserCreate
from src.foundation.system.repository.account_bind_repository import account_bind_repository
from src.models.platform import Role, AccountBind


class AuthService:
    def register(self, register_in: UserRegisterSchema) -> dict[str, Any]:
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

            if register_in.email:
                email_bind_count = account_bind_repository.count_by_identifier(1, register_in.email, tm.session)
                if email_bind_count >= 5:
                    raise BusinessException(
                        ResponseCode.PARAM_ERROR,
                        detail=f"该邮箱已绑定过多账号（最多绑定5个）",
                    )

            if register_in.phone:
                phone_bind_count = account_bind_repository.count_by_identifier(0, register_in.phone, tm.session)
                if phone_bind_count >= 5:
                    raise BusinessException(
                        ResponseCode.PARAM_ERROR,
                        detail=f"该手机号已绑定过多账号（最多绑定5个）",
                    )

            user_create = UserCreate(
                username=register_in.username,
                email=register_in.email,
                phone=register_in.phone,
                password=register_in.password,
                role_uuids=[],
            )

            new_user = user_repository.create_user(obj_in=user_create, session=tm.session)

            default_role = tm.session.execute(
                select(Role).where(Role.code == RoleCodeConst.PLATFORM_NORMAL_USER.value)
            ).scalar_one_or_none()
            if default_role:
                user_repository.update_roles(new_user, [str(default_role.uuid)], session=tm.session)
                logger.info(f"用户 {register_in.username} 自动分配默认角色: {RoleCodeConst.PLATFORM_NORMAL_USER.value}")

            tm.commit()

        result = {
            "uuid": new_user.uuid,
            "username": new_user.username,
            "email": register_in.email,
            "phone": register_in.phone,
            "created_at": new_user.created_at,
        }

        logger.info(f"用户注册成功: username={register_in.username}, user_id={new_user.id}")

        if settings.AUTO_LOGIN_AFTER_REGISTER:
            tokens = self._generate_tokens(new_user)
            self._store_tokens(new_user.id, tokens["access_token"], tokens["refresh_token"])
            result.update(tokens)
            result["token_type"] = "bearer"
            result["expires_in"] = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

        return result

    def login_by_account_and_password(self, req: LoginByPasswordStep1Request, client_ip: str) -> dict[str, Any]:
        account = req.account
        login_type = self._detect_login_type(account)
        logger.info(f"用户第一步登录尝试: identifier={account}, login_type={login_type}")

        user_list = self._verify_credentials(account, req.password, login_type)

        if not user_list:
            raise BusinessException(ResponseCode.LOGIN_FAILED, "账号或密码错误")

        if len(user_list) == 1:
            return self._handle_single_account_login(user_list[0], client_ip)

        return self._handle_multi_account_login(user_list)

    def select_user(self, temp_token: str, user_uuid: str, client_ip: str) -> dict[str, Any]:
        logger.info(f"用户选择账号: temp_token={temp_token}, user_uuid={user_uuid}")

        temp_data = self._validate_temp_token(temp_token)
        users = temp_data.get("users", [])

        selected_user = next((u for u in users if str(u["uuid"]) == user_uuid), None)
        if not selected_user:
            raise BusinessException(ResponseCode.FORBIDDEN, "用户不在可选择列表中")

        # 验证通过后立即删除临时令牌，防止重复使用
        token_manager.revoke_temp_login_token(temp_token)

        with TransactionManager() as tm:
            query = user_repository._apply_soft_delete_filter(
                select(user_repository.model).where(user_repository.model.uuid == UUID(user_uuid))
            )
            result = tm.session.execute(query)
            db_user = result.scalars().first()

            if not db_user:
                raise BusinessException(ResponseCode.NOT_FOUND, "用户不存在")
            if not db_user.is_active:
                raise BusinessException(ResponseCode.FORBIDDEN, "用户已被禁用")

            user_repository.update_last_login(db_user.id, client_ip, session=tm.session)
            tm.commit()

        return self._build_login_result(db_user, tm.session)

    def refresh_token(self, refresh_request: RefreshTokenRequest) -> dict[str, Any]:
        refresh_data = token_manager.get_refresh_token_data(refresh_request.refresh_token)
        if not refresh_data:
            raise BusinessException(ResponseCode.UNAUTHORIZED, "无效的Token")

        payload = verify_token(refresh_request.refresh_token, token_type="refresh")
        user_id = payload["user_id"]
        tenant_id = payload.get("tenant_id")
        member_id = payload.get("member_id")

        with TransactionManager() as tm:
            user = user_repository.get(id=user_id, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.NOT_FOUND, "用户不存在")
            if not user.is_active:
                raise BusinessException(ResponseCode.FORBIDDEN, "用户已被禁用")

        old_access_token = refresh_data.get("linked_access")
        if old_access_token:
            token_manager.revoke_access_token(old_access_token)
        token_manager.revoke_refresh_token(refresh_request.refresh_token)

        tokens = self._generate_tokens(user, tenant_id, member_id)
        self._store_tokens(user.id, tokens["access_token"], tokens["refresh_token"])

        logger.info(f"Token刷新成功: user_id={user_id}, tenant_id={tenant_id}, member_id={member_id}")

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
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

    def _detect_login_type(self, account: str) -> str:
        if re.match(r'^1[3-9]\d{9}$', account):
            return "phone"
        elif re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', account):
            return "email"
        return "username"

    def _verify_credentials(self, account: str, password: str, login_type: str) -> List[dict]:
        with TransactionManager() as tm:
            if login_type == "username":
                return auth_repository.login_by_username_and_password(account, password, session=tm.session)
            else:
                return auth_repository.login_by_account_and_password(account, password, session=tm.session)

    def _generate_tokens(self, user, tenant_id: int = None, member_id: int = None) -> dict[str, str]:
        access_token, refresh_token = create_token_pair(
            user_id=user.id,
            user_uuid=str(user.uuid),
            username=user.username,
            tenant_id=tenant_id,
            member_id=member_id,
        )
        return {"access_token": access_token, "refresh_token": refresh_token}

    def _store_tokens(self, user_id: int, access_token: str, refresh_token: str) -> None:
        access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        token_manager.store_access_token(access_token, user_id, access_ttl)
        token_manager.store_refresh_token(refresh_token, user_id, access_token, refresh_ttl)
        token_manager.add_user_token(user_id, access_token, refresh_token, refresh_ttl)

    def _generate_temp_token(self, users: List[dict]) -> str:
        return token_manager.store_temp_login_token(
            user_id=0,
            username="",
            users=users,
            tenant_memberships=[]
        )

    def _validate_temp_token(self, temp_token: str) -> dict:
        temp_data = token_manager.get_temp_login_token(temp_token)
        if not temp_data:
            raise BusinessException(ResponseCode.UNAUTHORIZED, "无效的临时登录凭证")
        return temp_data

    def _handle_single_account_login(self, user: dict, client_ip: str) -> dict[str, Any]:
        user_uuid = user["uuid"]

        with TransactionManager() as tm:
            query = user_repository._apply_soft_delete_filter(
                select(user_repository.model).where(user_repository.model.uuid == user_uuid)
            )
            result = tm.session.execute(query)
            db_user = result.scalars().first()

            user_repository.update_last_login(db_user.id, client_ip, session=tm.session)
            tm.commit()

        logger.info(f"用户登录成功（单账号）: user_uuid={user_uuid}")
        return self._build_login_result(db_user, tm.session)

    def _handle_multi_account_login(self, user_list: List[dict]) -> dict[str, Any]:
        temp_token = self._generate_temp_token(user_list)
        if not temp_token:
            raise BusinessException(ResponseCode.SERVER_ERROR, "生成临时登录凭证失败")

        logger.info(f"用户登录成功（多账号）: user_count={len(user_list)}")
        return {
            "temp_token": temp_token,
            "users": user_list,
        }

    def _build_login_result(self, user, session = None) -> dict[str, Any]:
        tokens = self._generate_tokens(user)
        self._store_tokens(user.id, tokens["access_token"], tokens["refresh_token"])

        email = None
        phone = None
        if session:
            binds_query = select(AccountBind).where(
                AccountBind.user_id == user.id,
                AccountBind.status == "verified",
                AccountBind.delete_time.is_(None)
            )
            binds_result = session.execute(binds_query).scalars().all()
            for bind in binds_result:
                if bind.bind_type == 1:
                    email = bind.identifier
                elif bind.bind_type == 0:
                    phone = bind.identifier

        user_info = {
            "uuid": str(user.uuid),
            "username": user.username,
            "email": email,
            "phone": phone,
            "alias": user.alias,
            "avatar": user.avatar,
            "gender": user.gender,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "last_login_ip": user.last_login_ip,
        }

        return {
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_info,
        }


auth_service = AuthService()
