
import jwt
import secrets
import string
from passlib.context import CryptContext
from datetime import datetime, timedelta, UTC
from src.core.config import settings


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_password() -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(12))
    return password


def create_jwt_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def parse_jwt_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


def create_access_token(*, data: dict):
    """创建访问令牌"""
    payload = data.copy()
    payload["token_type"] = "access"
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
    from fastapi import HTTPException
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("token_type") != token_type:
            raise HTTPException(status_code=401, detail="令牌类型无效")

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="令牌无效")


def create_token_pair(
    user_id: int, username: str
) -> tuple[str, str]:
    """创建访问令牌和刷新令牌对"""
    access_expire = datetime.now(UTC) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_payload = {
        "user_id": user_id,
        "username": username,
        "exp": access_expire,
        "token_type": "access",
    }
    access_token = create_access_token(data=access_payload)

    refresh_token = create_refresh_token(user_id, username)

    return access_token, refresh_token


def gen_perm_code(scene: str, resource: str, action: str) -> str:
    return f"{scene}:{resource}:{action}"


def check_perm_match(user_perms: set, required_perm: str) -> bool:
    return required_perm in user_perms

