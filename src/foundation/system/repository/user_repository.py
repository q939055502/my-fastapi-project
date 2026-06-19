import secrets
import string
from datetime import datetime
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from src.core.exceptions import BusinessException
from src.core.storage import BaseRepository
from src.foundation.iam.auth.schemas.login import LoginByPasswordStep1Request
from src.foundation.iam.auth.security import get_password_hash, verify_password
from src.foundation.system.schemas.user import UserCreate, UserUpdate
from src.models.platform import AccountBind, Role, RoleSubject, User


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):

    def __init__(self):
        super().__init__(model=User)

    def get_by_email(self, email: str, session: Session) -> User | None:
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

    def get_with_roles(self, id: int, session: Session) -> dict | None:
        """获取用户及其角色信息(通过 JOIN 查询)"""
        user_query = select(User).where(User.id == id)
        user_query = self._apply_soft_delete_filter(user_query)
        user_result = session.execute(user_query)
        user = user_result.scalars().first()

        if not user:
            return None

        # 查询用户的角色(通过 RoleSubject 关联)
        roles_query = select(Role).join(
            RoleSubject, Role.id == RoleSubject.role_id
        ).where(
            RoleSubject.subject_id == user.id,
            RoleSubject.subject_type == 0,  # 0=平台用户
            Role.delete_time.is_(None)
        )
        roles_result = session.execute(roles_query)
        roles = roles_result.scalars().all()

        # 查询用户的账号绑定
        binds_query = select(AccountBind).where(
            AccountBind.user_id == user.id,
            AccountBind.delete_time.is_(None)
        )
        binds_result = session.execute(binds_query)
        account_binds = binds_result.scalars().all()

        return {
            "user": user,
            "roles": roles,
            "account_binds": account_binds
        }

    def get_with_tenants(self, id: int, session: Session) -> dict | None:
        """获取用户及其租户信息(通过 JOIN 查询)"""
        from src.models.tenant import Member, Tenant

        user_query = select(User).where(User.id == id)
        user_query = self._apply_soft_delete_filter(user_query)
        user_result = session.execute(user_query)
        user = user_result.scalars().first()

        if not user:
            return None

        # 查询用户的租户成员关系
        members_query = select(Member, Tenant).join(
            Tenant, Member.tenant_id == Tenant.id
        ).where(
            Member.user_id == user.id,
            Member.delete_time.is_(None),
            Tenant.delete_time.is_(None)
        )
        members_result = session.execute(members_query)
        tenant_memberships = [
            {"member": row.Member, "tenant": row.Tenant}
            for row in members_result.all()
        ]

        # 查询用户的账号绑定
        binds_query = select(AccountBind).where(
            AccountBind.user_id == user.id,
            AccountBind.delete_time.is_(None)
        )
        binds_result = session.execute(binds_query)
        account_binds = binds_result.scalars().all()

        return {
            "user": user,
            "tenant_memberships": tenant_memberships,
            "account_binds": account_binds
        }

    def create_user(self, obj_in: UserCreate, session: Session) -> User:
        obj_in.password = get_password_hash(password=obj_in.password)

        obj_dict = obj_in.model_dump()
        obj_dict.pop('role_uuids', None)
        email = obj_dict.pop('email', None)
        phone = obj_dict.pop('phone', None)

        obj = self.create(obj_dict, session=session)

        # 创建邮箱绑定(如果提供了邮箱)
        if email:
            user_email_bind = AccountBind(
                user_id=obj.id,
                bind_type=1,
                identifier=email,
                is_default=True,
                status="verified",
                source="register"
            )
            session.add(user_email_bind)

        # 创建手机号绑定(如果提供了手机号)
        if phone:
            user_phone_bind = AccountBind(
                user_id=obj.id,
                bind_type=0,
                identifier=phone,
                is_default=True,
                status="verified",
                source="register"
            )
            session.add(user_phone_bind)

        if email or phone:
            session.flush()

        return obj

    def update_last_login(self, id: int, client_ip: str, session: Session) -> None:
        """更新用户最后登录时间和IP"""
        user = self.get(id=id, session=session)
        user.last_login = datetime.now()
        user.last_login_ip = client_ip

    def get_by_phone(self, phone: str, session: Session) -> User | None:
        query = select(User).join(
            AccountBind, User.id == AccountBind.user_id
        ).where(
            AccountBind.bind_type == 0,
            AccountBind.identifier == phone,
            AccountBind.status == "verified"
        )
        query = self._apply_soft_delete_filter(query)
        result = session.execute(query)
        return result.scalars().first()

    def authenticate(self, credentials: LoginByPasswordStep1Request, session: Session) -> Optional["User"]:
        from src.core.log import logger

        user = None

        # 按优先级查找用户:用户名 > 邮箱 > 手机号
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
            raise BusinessException(40100, "用户名、手机号、邮箱或密码错误")

        verified = verify_password(credentials.password, user.password)
        identifier = credentials.login_username or credentials.login_email or credentials.login_phone
        logger.info(f"Password verification - identifier: {identifier}, verified: {verified}")

        if not verified:
            logger.warning(f"Authentication failed - wrong password: {identifier}")
            self._delay_for_security()
            raise BusinessException(40100, "用户名、手机号、邮箱或密码错误")

        logger.info(f"User status check - identifier: {identifier}, is_active: {user.is_active}")

        if not user.is_active:
            logger.warning(f"Authentication failed - user disabled: {identifier}")
            raise BusinessException(40100, "用户已被禁用")

        logger.info(f"Authentication successful - identifier: {identifier}, user_id: {user.id}")
        return user

    def _delay_for_security(self):
        import time
        time.sleep(0.5)

    def update_roles(self, user_id: int, role_uuids: list, creator_id: int, session: Session) -> None:
        """更新用户角色(通过 RoleSubject 关联表)"""
        # 删除现有角色关联
        session.execute(
            delete(RoleSubject).where(
                RoleSubject.subject_id == user_id,
                RoleSubject.subject_type == 0  # 0=平台用户
            )
        )

        # 添加新的角色关联
        for role_uuid in role_uuids:
            role_query = select(Role).where(Role.uuid == role_uuid)
            role_query = self._apply_soft_delete_filter(role_query)
            role_obj = session.execute(role_query).scalars().first()
            if role_obj:
                role_subject = RoleSubject(
                    subject_id=user_id,
                    subject_type=0,  # 0=平台用户
                    role_id=role_obj.id,
                    creator_id=creator_id,
                    tenant_id=None  # 平台用户角色关联无租户
                )
                session.add(role_subject)

    def reset_password(self, user_id: int, session: Session) -> str:
        user_obj = self.get(id=user_id, session=session)
        if not user_obj:
            raise BusinessException(40401, "用户不存在")
        new_password = self._generate_secure_password()
        user_obj.password = get_password_hash(password=new_password)
        return new_password

    def _generate_secure_password(self, length: int = 12) -> str:
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        return password


user_repository = UserRepository()
