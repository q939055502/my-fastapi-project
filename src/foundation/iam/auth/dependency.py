"""
认证依赖注入模块

包含认证相关的依赖函数，用于FastAPI的依赖注入系统：
- Swagger UI 认证
- JWT 令牌认证
"""

import secrets

import jwt
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer
from src.core.config import settings
from src.core.enums.response_code import ResponseCode
from src.core.exceptions import BusinessException
from src.core.log import get_ctx_logger
from src.core.storage import TransactionManager
from src.foundation.iam.auth.token import token_manager

security = HTTPBasic()
bearer_scheme = HTTPBearer()


def get_current_username(
    credentials: HTTPBasicCredentials = Depends(security),
):
    correct_username = secrets.compare_digest(
        credentials.username, settings.SWAGGER_UI_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.SWAGGER_UI_PASSWORD
    )
    if not (correct_username and correct_password):
        raise BusinessException(ResponseCode.UNAUTHORIZED, "Authentication Required")
    return credentials.username


class AuthControl:
    @classmethod
    def authenticate_token(cls, access_token_str: str, raise_exc: bool = True) -> object | None:
        try:
            if not access_token_str:
                get_ctx_logger().debug("认证失败: 缺少token")
                if raise_exc:
                    raise BusinessException(ResponseCode.UNAUTHORIZED, "Missing authentication token")
                return None

            is_valid = token_manager.validate_access_token(access_token_str)
            get_ctx_logger().debug(f"Redis验证令牌结果: {is_valid}")

            if not is_valid:
                get_ctx_logger().debug("认证失败: 令牌无效或已撤销")
                if raise_exc:
                    raise BusinessException(ResponseCode.UNAUTHORIZED, "令牌已被撤销或失效")
                return None

            decode_data = jwt.decode(
                access_token_str,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            user_id = decode_data.get("user_id")
            get_ctx_logger().debug(f"JWT解码结果: user_id={user_id}")

            with TransactionManager() as tm:
                from sqlalchemy import select
                from src.models.platform import User

                result = tm.session.execute(
                    select(User)
                    .where(User.id == user_id)
                )
                user = result.scalars().first()
                get_ctx_logger().debug(f"数据库查询结果: user={user}")

            if not user:
                get_ctx_logger().debug(f"认证失败: 用户不存在 user_id={user_id}")
                if raise_exc:
                    raise BusinessException(ResponseCode.UNAUTHORIZED, "Authentication failed")
                return None

            get_ctx_logger().debug(f"用户认证成功: user_id={user.id}")
            return user
        except jwt.DecodeError as e:
            get_ctx_logger().debug(f"JWT解码错误: {str(e)}")
            if raise_exc:
                raise BusinessException(ResponseCode.UNAUTHORIZED, "无效的Token") from e
            return None
        except jwt.ExpiredSignatureError as e:
            get_ctx_logger().debug(f"JWT过期: {str(e)}")
            if raise_exc:
                raise BusinessException(ResponseCode.UNAUTHORIZED, "登录已过期") from e
            return None
        except BusinessException:
            if raise_exc:
                raise
            return None
        except Exception as e:
            get_ctx_logger().debug(f"认证异常: {str(e)}")
            if raise_exc:
                raise BusinessException(ResponseCode.UNAUTHORIZED, "认证失败") from e
            return None

    @classmethod
    def is_authed(cls, token: HTTPBearer = Depends(bearer_scheme)) -> object | None:
        get_ctx_logger().debug(f"is_authed 被调用，token credentials = {token.credentials[:50]}...")
        result = cls.authenticate_token(token.credentials)
        get_ctx_logger().debug(f"认证结果: {result}")
        return result

    @classmethod
    def get_auth_info(cls, token: HTTPBearer = Depends(bearer_scheme)) -> tuple[object | None, str]:
        user = cls.authenticate_token(token.credentials)
        return user, token.credentials
