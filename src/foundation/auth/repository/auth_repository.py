"""认证 Repository

提供用户登录相关的数据访问方法
"""

import time

from sqlalchemy import select
from sqlalchemy.orm import Session
from src.common.core.auth import verify_password
from src.common.core.constants import AccountBindStatusConst
from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.core.log import logger
from src.common.repository.base import GenericRepository
from src.models.platform import User
from src.models.platform.account_bind import AccountBind


class AuthRepository(GenericRepository[User, None, None]):
    """认证 Repository"""

    def __init__(self):
        super().__init__(User)

    def _delay_for_security(self):
        """安全延迟，防止暴力破解"""
        time.sleep(0.5)

    def login_by_username_and_password(self, username: str, password: str, session: Session) -> list[dict]:
        """
        通过用户名和密码登录

        Args:
            username: 用户名
            password: 密码
            session: 数据库会话

        Returns:
            list[dict]: 用户信息列表，每个用户包含：
                - uuid: 用户UUID
                - username: 用户名
                - alias: 别名
                - avatar: 头像
                - last_login: 最后登录时间
                - last_login_ip: 最后登录IP

        Raises:
            BusinessException: 用户不存在、密码错误或用户被禁用
        """
        logger.info(f"用户名登录尝试: username={username}")

        # 查询用户
        query = select(User).where(User.username == username)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        user = result.scalars().first()

        if not user:
            logger.warning(f"用户名登录失败 - 用户不存在: username={username}")
            self._delay_for_security()
            raise BusinessException(ResponseCode.LOGIN_FAILED, "用户名或密码错误")

        # 验证密码
        verified = verify_password(password, user.password)
        logger.info(f"密码验证 - username={username}, verified={verified}")

        if not verified:
            logger.warning(f"用户名登录失败 - 密码错误: username={username}")
            self._delay_for_security()
            raise BusinessException(ResponseCode.LOGIN_FAILED, "用户名或密码错误")

        # 检查用户状态
        if not user.is_active:
            logger.warning(f"用户名登录失败 - 用户被禁用: username={username}")
            raise BusinessException(ResponseCode.FORBIDDEN, "用户已被禁用")

        logger.info(f"用户名登录成功: username={username}, user_uuid={user.uuid}")
        return [{
            "uuid": str(user.uuid),
            "username": user.username,
            "alias": user.alias,
            "avatar": user.avatar,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "last_login_ip": user.last_login_ip,
        }]

    def login_by_account_and_password(self, account: str, password: str, session: Session) -> list[dict]:
        """
        通过账号（手机号/邮箱）和密码登录

        注：此方法只通过 AccountBind 查找，不处理用户名登录。
        用户名登录请使用 login_by_username_and_password 方法。

        Args:
            account: 手机号或邮箱
            password: 密码
            session: 数据库会话

        Returns:
            list[dict]: 密码匹配的用户列表，每个用户包含：
                - uuid: 用户UUID
                - username: 用户名
                - alias: 别名
                - avatar: 头像
                - last_login: 最后登录时间
                - last_login_ip: 最后登录IP
        """

        logger.info(f"账号登录尝试: account={account}")

        # 通过 AccountBind（手机号/邮箱）查找用户
        query = select(User).join(
            AccountBind, User.id == AccountBind.user_id
        ).where(
            AccountBind.identifier == account,
            AccountBind.status == AccountBindStatusConst.VERIFIED.value
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        users = result.scalars().all()

        # 收集密码匹配的用户
        matched_users = []
        for potential_user in users:
            if verify_password(password, potential_user.password):
                matched_users.append({
                    "uuid": str(potential_user.uuid),
                    "username": potential_user.username,
                    "alias": potential_user.alias,
                    "avatar": potential_user.avatar,
                    "last_login": potential_user.last_login.isoformat() if potential_user.last_login else None,
                    "last_login_ip": potential_user.last_login_ip,
                })
                logger.info(f"密码匹配成功: account={account}, user_uuid={potential_user.uuid}")

        if not matched_users:
            logger.warning(f"账号登录失败 - 密码不匹配: account={account}")
            self._delay_for_security()
            raise BusinessException(ResponseCode.LOGIN_FAILED, "账号或密码错误")
        return matched_users


# 全局实例
auth_repository = AuthRepository()
