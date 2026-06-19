"""
认证核心安全模块

包含密码哈希, JWT令牌的生成与验证等核心认证功能。
"""

import secrets
import string
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.core.exceptions import BusinessException

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_password() -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(12))
    return password


def create_access_token(*, data: dict, expires_delta: timedelta | None = None):
    payload = data.copy()
    payload["token_type"] = "access"
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire
    encoded_jwt = jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: int, user_uuid: str, username: str, tenant_id: int | None = None, member_id: int | None = None) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "user_id": user_id,
        "user_uuid": user_uuid,
        "username": username,
        "tenant_id": tenant_id,
        "member_id": member_id,
        "exp": expire,
        "token_type": "refresh",
    }

    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str, token_type: str = "access") -> dict:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("token_type") != token_type:
            raise BusinessException(40100, "无效的Token")

        return payload

    except jwt.ExpiredSignatureError:
        raise BusinessException(40100, "登录已过期") from None
    except jwt.InvalidTokenError:
        raise BusinessException(40100, "无效的Token") from None


def parse_jwt_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def create_token_pair(user_id: int, user_uuid: str, username: str, tenant_id: int | None = None, member_id: int | None = None) -> tuple[str, str]:
    access_payload = {
        "user_id": user_id,
        "user_uuid": user_uuid,
        "username": username,
        "tenant_id": tenant_id,
        "member_id": member_id,
    }
    access_token = create_access_token(data=access_payload)

    refresh_token = create_refresh_token(user_id, user_uuid, username, tenant_id, member_id)

    return access_token, refresh_token


def gen_perm_code(scene: str, resource: str, action: str) -> str:
    return f"{scene}:{resource}:{action}"


def check_perm_match(user_perms: set, required_perm: str) -> bool:
    return required_perm in user_perms
