"""
认证核心控制

只放纯认证逻辑，不含 FastAPI Depends 语法。
FastAPI 依赖注入统一由 src.foundation.iam.decorators 提供。
"""

import secrets

import jwt
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer

from src.core.config import settings
from src.core.exceptions import BusinessException
from src.core.log import get_ctx_logger
from src.core.storage import TransactionManager


security = HTTPBasic()


def get_current_username(
    credentials: HTTPBasicCredentials = None,
):
    if credentials is None:
        return None
    correct_username = secrets.compare_digest(
        credentials.username, settings.SWAGGER_UI_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.SWAGGER_UI_PASSWORD
    )
    if not (correct_username and correct_password):
        from fastapi import HTTPException
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class AuthControl:
    """认证控制类（纯逻辑，不含 Depends）

    - authenticate_token: 验证 access token 并返回 User 对象
    - 不带任何 FastAPI 依赖注入语法（如 Depends(...)）
    - FastAPI 依赖入口统一由 src.foundation.iam.decorators 提供:
        require_auth, require_permission(...)
    """

    @staticmethod
    def authenticate_token(access_token_str: str, raise_exc: bool = True) -> object | None:
        try:
            if not access_token_str:
                get_ctx_logger().debug("认证失败: 缺少token")
                if raise_exc:
                    raise BusinessException(40100, "Missing authentication token")
                return None

            from src.foundation.iam.auth.token import token_manager

            is_valid = token_manager.validate_access_token(access_token_str)
            get_ctx_logger().debug(f"Redis验证令牌结果: {is_valid}")

            if not is_valid:
                get_ctx_logger().debug("认证失败: 令牌无效或已撤销")
                if raise_exc:
                    raise BusinessException(40100, "令牌已被撤销或失效")
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
                    raise BusinessException(40100, "Authentication failed")
                return None

            get_ctx_logger().debug(f"用户认证成功: user_id={user.id}")
            return user
        except jwt.DecodeError as e:
            get_ctx_logger().debug(f"JWT解码错误: {str(e)}")
            if raise_exc:
                raise BusinessException(40100, "无效的Token") from e
            return None
        except jwt.ExpiredSignatureError as e:
            get_ctx_logger().debug(f"JWT过期: {str(e)}")
            if raise_exc:
                raise BusinessException(40100, "登录已过期") from e
            return None
        except BusinessException:
            if raise_exc:
                raise
            return None
        except Exception as e:
            get_ctx_logger().debug(f"认证异常: {str(e)}")
            if raise_exc:
                raise BusinessException(40100, "认证失败") from e
            return None
