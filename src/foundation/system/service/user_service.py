"""用户服务 - 个人操作

此服务包含用户对自己信息的操作：
- 获取个人信息
- 修改个人信息
- 修改密码
- 获取我的租户列表
"""

from typing import Any

from src.foundation.iam.auth.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from src.core.config import settings
from src.core.enums.response_code import ResponseCode
from src.core.exceptions import BusinessException
from src.core.log import logger
from src.core.storage.cache.cache_manager import clear_user_cache
from src.core.storage.transaction_manager import TransactionManager
from src.foundation.system.repository.account_bind_repository import (
    account_bind_repository,
)
from src.foundation.system.repository.user_repository import user_repository
from src.foundation.tenant.repository.member_repository import tenant_member_repository


class UserService:
    """用户服务 - 个人操作"""

    def get_my_profile(self, user_id: int) -> dict:
        """获取个人信息（仅用户表基本信息 + 账号绑定）"""
        with TransactionManager() as tm:
            user_obj = user_repository.get(id=user_id, session=tm.session)
            if not user_obj:
                raise BusinessException(ResponseCode.NOT_FOUND, detail="用户不存在")

            # 只返回需要的字段，避免暴露不必要的信息
            user_dict = {
                "uuid": str(user_obj.uuid),
                "username": user_obj.username,
                "alias": user_obj.alias,
                "avatar": user_obj.avatar,
                "gender": user_obj.gender,
                "is_active": user_obj.is_active,
                "last_login": user_obj.last_login,
                "last_login_ip": user_obj.last_login_ip,
                "created_at": user_obj.created_at,
                "remark": user_obj.remark,
            }

            # 添加 email 和 phone 字段，从 AccountBind 中获取
            user_dict["email"] = account_bind_repository.get_email(user_id, tm.session)
            user_dict["phone"] = account_bind_repository.get_phone(user_id, tm.session)

            return user_dict

    def update_my_profile(self, user_id: int, update_data: dict) -> dict:
        """修改个人信息

        Args:
            user_id: 用户ID
            update_data: 更新数据（只能修改允许的字段）

        Returns:
            dict: 更新后的用户信息
        """
        logger.info(f"用户修改个人信息: user_id={user_id}")

        with TransactionManager() as tm:
            user = user_repository.get(id=user_id, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.NOT_FOUND, detail="用户不存在")

            # 个人信息只能修改特定字段（不允许修改用户名、角色等）
            allowed_fields = {"alias", "avatar", "gender", "remark"}
            filtered_data = {k: v for k, v in update_data.items() if k in allowed_fields}

            if filtered_data:
                user_repository.update(id=user_id, obj_in=filtered_data, session=tm.session)
                tm.commit()
                # 重新获取用户对象（确保返回最新数据）
                user = user_repository.get(id=user_id, session=tm.session)

            # 只返回需要的字段，避免暴露不必要的信息
            user_dict = {
                "uuid": str(user.uuid),
                "username": user.username,
                "alias": user.alias,
                "avatar": user.avatar,
                "gender": user.gender,
                "is_active": user.is_active,
                "last_login": user.last_login,
                "last_login_ip": user.last_login_ip,
                "created_at": user.created_at,
                "remark": user.remark,
            }

            # 添加 email 和 phone 字段，从 AccountBind 中获取
            user_dict["email"] = account_bind_repository.get_email(user_id, tm.session)
            user_dict["phone"] = account_bind_repository.get_phone(user_id, tm.session)

            logger.info(f"用户个人信息修改成功: user_id={user_id}")
            return user_dict

    def change_my_password(self, user_id: int, old_password: str, new_password: str) -> bool:
        """修改自己的密码

        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码

        Returns:
            bool: 是否修改成功
        """
        logger.info(f"用户修改密码: user_id={user_id}")

        with TransactionManager() as tm:
            user = user_repository.get(id=user_id, session=tm.session)
            if not user:
                raise BusinessException(ResponseCode.NOT_FOUND, detail="用户不存在")

            if not verify_password(old_password, user.password):
                logger.warning(f"用户密码修改失败: 旧密码错误, user_id={user_id}")
                return False

            user.password = get_password_hash(new_password)
            tm.commit()

        clear_user_cache(user_id)
        logger.info(f"用户密码修改成功: user_id={user_id}")
        return True

    def get_my_tenants(self, user_id: int) -> list[dict]:
        """获取我的租户列表

        Args:
            user_id: 用户ID

        Returns:
            list[dict]: 租户列表
        """
        with TransactionManager() as tm:
            tenant_memberships = tenant_member_repository.get_user_tenants(user_id, session=tm.session)

            formatted_tenants = []
            for idx, tenant in enumerate(tenant_memberships):
                formatted_tenants.append({
                    "tenant_id": tenant["tenant_id"],
                    "tenant_name": tenant["tenant_name"],
                    "tenant_code": tenant["tenant_code"],
                    "is_owner": tenant["is_owner"],
                    "is_default": idx == 0,
                })

            return formatted_tenants

    def switch_tenant(self, user_id: int, tenant_id: int) -> dict[str, Any]:
        """已登录用户切换租户

        Args:
            user_id: 用户ID
            tenant_id: 要切换的租户ID

        Returns:
            dict: 新的令牌
        """
        logger.info(f"用户切换租户: user_id={user_id}, tenant_id={tenant_id}")

        with TransactionManager() as tm:
            tenant_memberships = tenant_member_repository.get_user_tenants(user_id, session=tm.session)

            selected_tenant = next(
                (t for t in tenant_memberships if t["tenant_id"] == tenant_id),
                None
            )

            if not selected_tenant:
                raise BusinessException(ResponseCode.FORBIDDEN, "您不属于该租户")

            user = user_repository.get(id=user_id, session=tm.session)

        access_token, refresh_token = create_token_pair(
            user_id=user_id,
            user_uuid=str(user.uuid),
            username=user.username,
            tenant_id=tenant_id,
            member_id=selected_tenant.get("member_id")
        )

        access_ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        refresh_ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

        token_manager.store_access_token(access_token, user_id, access_ttl)
        token_manager.store_refresh_token(refresh_token, user_id, access_token, refresh_ttl)
        token_manager.add_user_token(user_id, access_token, refresh_token, refresh_ttl)

        logger.info(f"用户切换租户成功: user_id={user_id}, tenant_id={tenant_id}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": access_ttl,
        }


user_service = UserService()