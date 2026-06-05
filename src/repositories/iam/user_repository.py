import secrets
import string
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from src.core.auth import get_password_hash, verify_password
from src.core.enums.response_code import ResponseCode
from src.core.exceptions import BusinessException
from src.models.iam import User
from src.repositories.base import GenericRepository
from src.schemas.auth.login import LoginRequest
from src.schemas.iam.user import UserCreate, UserUpdate

from .role_repository import role_repository


class UserRepository(GenericRepository[User, UserCreate, UserUpdate]):

    def __init__(self):
        super().__init__(model=User)

    def get_by_email(self, email: str, session: Session) -> User | None:
        from src.models.iam.user_bind import UserBind
        query = select(User).join(
            UserBind, User.id == UserBind.user_id
        ).where(
            UserBind.bind_type == 1,
            UserBind.value == email,
            UserBind.status == "verified"
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_email_with_deleted(self, email: str, session: Session) -> User | None:
        from src.models.iam.user_bind import UserBind
        result = session.execute(
            select(User).join(
                UserBind, User.id == UserBind.user_id
            ).where(
                UserBind.bind_type == 1,
                UserBind.value == email,
                UserBind.status == "verified"
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
            query.options(selectinload(User.roles))
        )
        return result.scalars().first()

    def get_with_tenants(self, id: int, session: Session) -> User | None:
        query = select(User).where(User.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(
            query.options(selectinload(User.tenant_memberships))
        )
        return result.scalars().first()

    def create_user(self, obj_in: UserCreate, session: Session) -> User:
        obj_in.password = get_password_hash(password=obj_in.password)

        obj_dict = obj_in.model_dump()
        obj_dict.pop('role_ids', None)
        email = obj_dict.pop('email', None)

        obj = self.create(obj_dict, session=session)

        if email:
            from src.models.iam.user_bind import UserBind
            user_bind = UserBind(
                user_id=obj.id,
                bind_type=1,
                value=email,
                is_default=1,
                status="verified",
                source="register"
            )
            session.add(user_bind)
            session.flush()

        return obj

    def update_last_login(self, id: int, session: Session) -> None:
        user = self.get(id=id, session=session)
        user.last_login = datetime.now()

    def authenticate(self, credentials: LoginRequest, session: Session) -> Optional["User"]:
        from src.core.log import logger

        user = self.get_by_username(credentials.username, session=session)
        logger.info(f"Authenticate attempt - username: {credentials.username}, user_found: {user is not None}")

        if not user:
            logger.warning(f"Authentication failed - user not found: {credentials.username}")
            self._delay_for_security()
            raise BusinessException(ResponseCode.UNAUTHORIZED, "用户名或密码错误")

        verified = verify_password(credentials.password, user.password)
        logger.info(f"Password verification - username: {credentials.username}, verified: {verified}")

        if not verified:
            logger.warning(f"Authentication failed - wrong password: {credentials.username}")
            self._delay_for_security()
            raise BusinessException(ResponseCode.UNAUTHORIZED, "用户名或密码错误")

        logger.info(f"User status check - username: {credentials.username}, is_active: {user.is_active}")

        if not user.is_active:
            logger.warning(f"Authentication failed - user disabled: {credentials.username}")
            raise BusinessException(ResponseCode.UNAUTHORIZED, "用户已被禁用")

        logger.info(f"Authentication successful - username: {credentials.username}, user_id: {user.id}")
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
