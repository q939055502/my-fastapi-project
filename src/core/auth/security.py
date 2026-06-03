
"""
认证核心安全模块

包含密码哈希、JWT令牌的生成与验证等核心认证功能。
"""

import secrets
import string
from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from src.core.config import settings
from src.core.enums.response_code import ResponseCode
from src.core.exceptions.exception import BusinessException

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """密码哈希"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """密码验证"""
    return pwd_context.verify(plain_password, hashed_password)


def generate_password() -> str:
    """生成随机密码"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(12))
    return password


def create_access_token(*, data: dict, expires_delta: timedelta | None = None):
    """创建访问令牌"""
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


def create_refresh_token(user_id: int, username: str) -> str:
    """创建刷新令牌"""
    expire = datetime.now(UTC) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    payload = {
        "user_id": user_id,
        "username": username,
        "exp": expire,
        "token_type": "refresh",
    }

    return jwt.encode(
        payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def verify_token(token: str, token_type: str = "access") -> dict:
    """验证令牌并返回载荷"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("token_type") != token_type:
            raise BusinessException(ResponseCode.UNAUTHORIZED, "无效的Token")

        return payload

    except jwt.ExpiredSignatureError:
        raise BusinessException(ResponseCode.UNAUTHORIZED, "登录已过期") from None
    except jwt.InvalidTokenError:
        raise BusinessException(ResponseCode.UNAUTHORIZED, "无效的Token") from None


def parse_jwt_token(token: str) -> dict | None:
    """解析JWT令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def create_token_pair(user_id: int, username: str) -> tuple[str, str]:
    """创建访问令牌和刷新令牌对"""
    access_payload = {
        "user_id": user_id,
        "username": username,
    }
    access_token = create_access_token(data=access_payload)

    refresh_token = create_refresh_token(user_id, username)

    return access_token, refresh_token


def gen_perm_code(scene: str, resource: str, action: str) -> str:
    """生成权限码"""
    return f"{scene}:{resource}:{action}"


def check_perm_match(user_perms: set, required_perm: str) -> bool:
    """检查权限匹配"""
    return required_perm in user_perms
