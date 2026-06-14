import re
from typing import Any

from src.common.core.auth import create_token_pair, token_manager, verify_token
from src.common.core.config import settings
from src.common.core.constants import RoleCodeConst
from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.log import logger
from src.common.core.storage import TransactionManager
from src.foundation.auth.repository.auth_repository import auth_repository
from src.foundation.auth.schemas.login import LoginByPasswordStep1Request
from src.foundation.auth.schemas.register import UserRegisterSchema
from src.foundation.auth.schemas.token import RefreshTokenRequest
from src.foundation.platform.repository.role_repository import role_repository
from src.foundation.platform.repository.user_repository import user_repository
from src.foundation.platform.schemas.user import UserCreate


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
                role_uuids=[],
            )

            new_user = user_repository.create_user(obj_in=user_create, session=tm.session)

            default_role = tm.session.execute(
                role_repository.model.__table__.select()
                .where(role_repository.model.code == RoleCodeConst.PLATFORM_NORMAL_USER.value)
            ).first()
            if default_role:
                user_repository.update_roles(new_user, [default_role.uuid], session=tm.session)
                logger.info(f"用户 {register_in.username} 自动分配默认角色: {RoleCodeConst.PLATFORM_NORMAL_USER.value}")

            tm.commit()

        result = {
            "uuid": new_user.uuid,
            "username": new_user.username,
            "email": register_in.email,
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

    def login_by_account_and_password(self, req: LoginByPasswordStep1Request, client_ip: str) -> dict[str, Any]:
        """第一步登录：验证用户密码，返回凭证

        如果只有一个账号匹配，直接返回正式业务令牌；
        如果有多个账号匹配（同一手机号/邮箱绑定多个账号），返回临时凭证和用户列表供选择。

        Args:
            req: 登录请求
            client_ip: 客户端IP
        """

        account = req.account
        login_type = "username"
        # 1. 判断是否为手机号
        if re.match(r'^1[3-9]\d{9}$', account):
            login_type = "phone"
        # 2. 判断是否为邮箱
        elif re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', account):
            login_type = "email"

        identifier = account
        logger.info(f"用户第一步登录尝试: identifier={identifier}")

        with TransactionManager() as tm:
            if login_type == "username":
                user_list = auth_repository.login_by_username_and_password(account, req.password, session=tm.session)
            else:
                user_list = auth_repository.login_by_account_and_password(account, req.password, session=tm.session)

            if not user_list:
                raise BusinessException(ResponseCode.LOGIN_FAILED, "账号或密码错误")

            # 单账号登录 - 直接返回正式令牌
            if len(user_list) == 1:
                user = user_list[0]
                user_uuid = user["uuid"]
                # 通过 uuid 获取用户 ID 用于内部操作
                db_user = user_repository.get_by_uuid(user_uuid, session=tm.session)
                user_repository.update_last_login(db_user.id, client_ip, session=tm.session)
                tm.commit()

                access_token, refresh_token = create_token_pair(
                    user_id=db_user.id,
                    username=user["username"],
                )

                access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
                refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

                token_manager.store_access_token(access_token, db_user.id, access_ttl)
                token_manager.store_refresh_token(refresh_token, db_user.id, access_token, refresh_ttl)
                token_manager.add_user_token(db_user.id, access_token, refresh_token, refresh_ttl)

                logger.info(f"用户登录成功（单账号）: identifier={identifier}, user_uuid={user_uuid}")

                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": access_ttl,
                    "user": user,
                }

            # 多账号登录 - 返回临时凭证供选择
            else:
                temp_token = token_manager.store_temp_login_token(
                    user_id=0,  # 多账号时暂不存储具体用户ID
                    username="",
                    users=user_list,  # 存储用户列表供选择
                    tenant_memberships=[]
                )

                if not temp_token:
                    raise BusinessException(ResponseCode.SERVER_ERROR, "生成临时登录凭证失败")

                logger.info(f"用户登录成功（多账号）: identifier={identifier}, user_count={len(user_list)}")

                return {
                    "temp_token": temp_token,
                    "users": user_list,
                }

    def select_user(self, temp_token: str, user_uuid: str, client_ip: str) -> dict[str, Any]:
        """第二步登录：多账号场景下选择用户，返回正式业务令牌

        Args:
            temp_token: 临时凭证
            user_uuid: 选择的用户UUID
            client_ip: 客户端IP

        Returns:
            dict: 登录结果，与单账号登录返回格式一致
        """
        from uuid import UUID

        logger.info(f"用户选择账号: temp_token={temp_token}, user_uuid={user_uuid}")

        # 1. 验证临时凭证
        temp_data = token_manager.get_temp_login_token(temp_token)
        if not temp_data:
            raise BusinessException(ResponseCode.UNAUTHORIZED, "无效的临时登录凭证")

        # 2. 验证用户是否在临时凭证的用户列表中
        users = temp_data.get("users", [])
        selected_user = next((u for u in users if str(u["uuid"]) == user_uuid), None)
        if not selected_user:
            raise BusinessException(ResponseCode.FORBIDDEN, "用户不在可选择列表中")

        # 3. 验证用户仍然有效（未被禁用等）
        with TransactionManager() as tm:
            user = user_repository.get_by_uuid(user_uuid, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.NOT_FOUND, "用户不存在")
            if not user.is_active:
                raise BusinessException(ResponseCode.FORBIDDEN, "用户已被禁用")

            # 4. 更新最后登录信息
            user_repository.update_last_login(user.id, client_ip, session=tm.session)
            tm.commit()

        # 5. 生成正式令牌
        access_token, refresh_token = create_token_pair(
            user_id=user.id,
            username=user.username,
        )

        access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        token_manager.store_access_token(access_token, user.id, access_ttl)
        token_manager.store_refresh_token(refresh_token, user.id, access_token, refresh_ttl)
        token_manager.add_user_token(user.id, access_token, refresh_token, refresh_ttl)

        logger.info(f"用户选择账号成功: user_uuid={user_uuid}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": access_ttl,
            "user": selected_user,
        }

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

        access_token, new_refresh_token = create_token_pair(
            user_id=user.id, username=user.username, tenant_id=tenant_id, member_id=member_id
        )

        access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        token_manager.store_access_token(access_token, user.id, access_ttl)
        token_manager.store_refresh_token(new_refresh_token, user.id, access_token, refresh_ttl)
        token_manager.add_user_token(user.id, access_token, new_refresh_token, refresh_ttl)

        logger.info(f"Token刷新成功: user_id={user_id}, tenant_id={tenant_id}, member_id={member_id}")

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
