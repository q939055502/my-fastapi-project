import secrets
import string
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from src.common.core.auth import get_password_hash, verify_password
from src.common.core.enums.response_code import ResponseCode
from src.common.core.exceptions import BusinessException
from src.common.repository.base import GenericRepository
from src.models.platform import User
from src.modules.auth.schemas.login import LoginByPasswordStep1Request
from src.modules.platform.schemas.user import UserCreate, UserUpdate

from .role_repository import role_repository


class UserRepository(GenericRepository[User, UserCreate, UserUpdate]):

    def __init__(self):
        super().__init__(model=User)

    def get_by_email(self, email: str, session: Session) -> User | None:
        from src.models.platform.account_bind import AccountBind
        query = select(User).join(
            AccountBind, User.id == AccountBind.user_id
        ).where(
            AccountBind.bind_type == 1,
            AccountBind.identifier == email,
            AccountBind.status == "verified"
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_email_with_deleted(self, email: str, session: Session) -> User | None:
        from src.models.platform.account_bind import AccountBind
        result = session.execute(
            select(User).join(
                AccountBind, User.id == AccountBind.user_id
            ).where(
                AccountBind.bind_type == 1,
                AccountBind.identifier == email,
                AccountBind.status == "verified"
            )
        )
        return result.scalars().first()

    def get_by_username(self, username: str, session: Session) -> User | None:
        query = select(User).where(User.username == username)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_username_with_deleted(self, username: str, session: Session) -> User | None:
        result = session.execute(
            select(User).where(User.username == username)
        )
        return result.scalars().first()

    def get_with_roles(self, id: int, session: Session) -> User | None:
        query = select(User).where(User.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(
            query.options(
                selectinload(User.roles),
                selectinload(User.account_binds)
            )
        )
        return result.scalars().first()

    def get_with_tenants(self, id: int, session: Session) -> User | None:
        query = select(User).where(User.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(
            query.options(
                selectinload(User.tenant_memberships),
                selectinload(User.account_binds)
            )
        )
        return result.scalars().first()

    def create_user(self, obj_in: UserCreate, session: Session) -> User:
        obj_in.password = get_password_hash(password=obj_in.password)

        obj_dict = obj_in.model_dump()
        obj_dict.pop('role_ids', None)
        email = obj_dict.pop('email', None)

        obj = self.create(obj_dict, session=session)

        if email:
            from src.models.platform.account_bind import AccountBind
            user_bind = AccountBind(
                user_id=obj.id,
                bind_type=1,
                identifier=email,
                is_default=1,
                status="verified",
                source="register"
            )
            session.add(user_bind)
            session.flush()

        return obj

    def update_last_login(self, id: int, client_ip: str, session: Session) -> None:
        """更新用户最后登录时间和IP

        Args:
            id: 用户ID
            client_ip: 客户端IP
            session: 数据库会话
        """
        user = self.get(id=id, session=session)
        user.last_login = datetime.now()
        user.last_login_ip = client_ip

    def get_by_phone(self, phone: str, session: Session) -> User | None:
        from src.models.platform.account_bind import AccountBind
        query = select(User).join(
            AccountBind, User.id == AccountBind.user_id
        ).where(
            AccountBind.bind_type == 2,
            AccountBind.identifier == phone,
            AccountBind.status == "verified"
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def authenticate(self, credentials: LoginByPasswordStep1Request, session: Session) -> Optional["User"]:
        from src.common.core.log import logger

        user = None

        # 按优先级查找用户：用户名 > 邮箱 > 手机号
        if credentials.login_username:
            user = self.get_by_username(credentials.login_username, session)
            logger.info(f"Authenticate attempt - username: {credentials.login_username}, user_found: {user is not None}")
        elif credentials.login_email:
            user = self.get_by_email(credentials.login_email, session)
            logger.info(f"Authenticate attempt - email: {credentials.login_email}, user_found: {user is not None}")
        elif credentials.login_phone:
            user = self.get_by_phone(credentials.login_phone, session)
            logger.info(f"Authenticate attempt - phone: {credentials.login_phone}, user_found: {user is not None}")

        if not user:
            logger.warning("Authentication failed - user not found")
            self._delay_for_security()
            raise BusinessException(ResponseCode.UNAUTHORIZED, "用户名/手机号/邮箱或密码错误")

        verified = verify_password(credentials.password, user.password)
        identifier = credentials.login_username or credentials.login_email or credentials.login_phone
        logger.info(f"Password verification - identifier: {identifier}, verified: {verified}")

        if not verified:
            logger.warning(f"Authentication failed - wrong password: {identifier}")
            self._delay_for_security()
            raise BusinessException(ResponseCode.UNAUTHORIZED, "用户名/手机号/邮箱或密码错误")

        logger.info(f"User status check - identifier: {identifier}, is_active: {user.is_active}")

        if not user.is_active:
            logger.warning(f"Authentication failed - user disabled: {identifier}")
            raise BusinessException(ResponseCode.UNAUTHORIZED, "用户已被禁用")

        logger.info(f"Authentication successful - identifier: {identifier}, user_id: {user.id}")
        return user

    def _delay_for_security(self):
        import time
        time.sleep(0.5)

    def update_roles(self, user: User, role_ids: list[int], session: Session) -> None:
        user.roles.clear()
        for role_id in role_ids:
            role_obj = role_repository.get(id=role_id, session=session)
            if role_obj:
                user.roles.append(role_obj)

    def reset_password(self, user_id: int, session: Session) -> str:
        user_obj = self.get(id=user_id, session=session)
        if not user_obj:
            raise BusinessException(ResponseCode.ENTITY_NOT_FOUND, "用户不存在")
        new_password = self._generate_secure_password()
        user_obj.password = get_password_hash(password=new_password)
        return new_password

    def _generate_secure_password(self, length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        return password


user_repository = UserRepository()
