import secrets
import string
from datetime import datetime
from typing import Optional

from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.core.storage.generic_repository import GenericRepository
from src.models.sys import User
from src.schemas.sys.login import CredentialsSchema
from src.schemas.sys.users import UserCreate, UserUpdate
from src.core.security import get_password_hash, verify_password

from .role_repository import role_repository


class UserRepository(GenericRepository[User, UserCreate, UserUpdate]):
    
    def __init__(self):
        super().__init__(model=User)

    def get_by_email(self, email: str, session: Session) -> User | None:
        query = select(User).where(User.email == email)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def get_by_email_with_deleted(self, email: str, session: Session) -> User | None:
        result = session.execute(
            select(User).where(User.email == email)
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

    def get_with_roles(self, id: int, session: Session) -> Optional[User]:
        query = select(User).where(User.id == id)
        query = self._apply_soft_delete_filter(query)
        result = session.execute(
            query.options(selectinload(User.roles))
        )
        return result.scalars().first()

    def create_user(self, obj_in: UserCreate, session: Session) -> User:
        obj_in.password = get_password_hash(password=obj_in.password)
        
        obj_dict = obj_in.model_dump()
        obj_dict.pop('role_ids', None)
        
        obj = self.create(obj_dict, session=session)
        return obj

    def update_last_login(self, id: int, session: Session) -> None:
        user = self.get(id=id, session=session)
        user.last_login = datetime.now()

    def authenticate(self, credentials: CredentialsSchema, session: Session) -> Optional["User"]:
        user = self.get_by_username(credentials.username, session=session)
        if not user:
            raise HTTPException(status_code=400, detail="无效的用户名")
        verified = verify_password(credentials.password, user.password)
        if not verified:
            raise HTTPException(status_code=400, detail="密码错误")
        if not user.is_active:
            raise HTTPException(status_code=400, detail="用户已被禁用")
        return user

    def update_roles(self, user: User, role_ids: list[int], session: Session) -> None:
        user.roles.clear()
        for role_id in role_ids:
            role_obj = role_repository.get(id=role_id, session=session)
            if role_obj:
                user.roles.append(role_obj)

    def reset_password(self, user_id: int, session: Session) -> str:
        user_obj = self.get(id=user_id, session=session)
        if not user_obj:
            raise HTTPException(status_code=404, detail="用户不存在")
        new_password = self._generate_secure_password()
        user_obj.password = get_password_hash(password=new_password)
        return new_password

    def _generate_secure_password(self, length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        return password


user_repository = UserRepository()
