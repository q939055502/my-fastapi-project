"""认证 Repository

提供用户登录相关的数据访问方法。
"""

import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.constants import AccountBindStatusConst
from src.core.exceptions import BusinessException
from src.core.log import logger
from src.core.storage import BaseRepository
from src.foundation.iam.auth import verify_password
from src.models.platform import User
from src.models.platform.auth import AccountBind


class AuthRepository(BaseRepository[User, None, None]):
    def __init__(self):
        super().__init__(User)

    def _delay_for_security(self):
        time.sleep(0.5)

    def login_by_username_and_password(self, username: str, password: str, session: Session) -> list[dict]:
        logger.info(f"用户名登录尝试: username={username}")

        query = select(User).where(User.username == username)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        user = result.scalars().first()

        if not user:
            logger.warning(f"用户名登录失败 - 用户不存在: username={username}")
            self._delay_for_security()
            raise BusinessException(40104, "用户名或密码错误")

        verified = verify_password(password, user.password)
        logger.info(f"密码验证 - username={username}, verified={verified}")

        if not verified:
            logger.warning(f"用户名登录失败 - 密码错误: username={username}")
            self._delay_for_security()
            raise BusinessException(40104, "用户名或密码错误")

        if not user.is_active:
            logger.warning(f"用户名登录失败 - 用户被禁用: username={username}")
            raise BusinessException(40300, "用户已被禁用")

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
        logger.info(f"账号登录尝试: account={account}")

        query = select(User).join(
            AccountBind, User.id == AccountBind.user_id
        ).where(
            AccountBind.identifier == account,
            AccountBind.status == AccountBindStatusConst.VERIFIED.value
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        users = result.scalars().all()

        matched_users = []
        for potential_user in users:
            if verify_password(password, potential_user.password):
                matched_users.append({
                    "uuid": str(potential_user.uuid),
                    "username": potential_user.username,
                    "alias": potential_user.alias,
                    "avatar": potential_user.avatar,
                    "gender": potential_user.gender,
                    "is_active": potential_user.is_active,
                    "created_at": potential_user.created_at,
                    "last_login": potential_user.last_login.isoformat() if potential_user.last_login else None,
                    "last_login_ip": potential_user.last_login_ip,
                })
                logger.info(f"密码匹配成功: account={account}, user_uuid={potential_user.uuid}")

        if not matched_users:
            logger.warning(f"账号登录失败 - 密码不匹配: account={account}")
            self._delay_for_security()
            raise BusinessException(40104, "账号或密码错误")
        return matched_users


auth_repository = AuthRepository()
