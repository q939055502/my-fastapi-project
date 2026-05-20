
import re
import secrets
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPBearer

from src.core.ctx import CTX_USER_ID
from src.core.config import settings
from src.core.storage import UnitOfWork, token_manager
from src.core.log import logger


"""
依赖注入模块

包含认证和权限控制相关的依赖函数，用于FastAPI的依赖注入系统。主要功能：
1. Swagger UI 认证
2. JWT 令牌认证
3. API 权限控制
4. 智能体权限控制
"""


# 安全方案实例
security = HTTPBasic()  # 用于Swagger UI的基本认证
bearer_scheme = HTTPBearer()  # 用于JWT令牌认证


def get_current_username(
    credentials: HTTPBasicCredentials = Depends(security),
):
    """获取当前用户名（用于Swagger UI认证）
    
    Args:
        credentials: HTTP基本认证凭据
        
    Returns:
        str: 认证成功的用户名
        
    Raises:
        HTTPException: 认证失败时抛出401错误
    """
    correct_username = secrets.compare_digest(
        credentials.username, settings.SWAGGER_UI_USERNAME
    )
    correct_password = secrets.compare_digest(
        credentials.password, settings.SWAGGER_UI_PASSWORD
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Required",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


class AuthControl:
    """认证控制器
    
    处理用户认证相关的逻辑，包括JWT令牌验证和用户信息获取。
    """

    @classmethod
    def authenticate_token(cls, access_token_str: str, raise_exc: bool = True) -> Optional[object]:
        """验证访问令牌并返回用户（接受字符串token）
        
        Args:
            access_token_str: 访问令牌字符串
            raise_exc: 失败时是否抛出异常（False用于审计日志等场景）
            
        Returns:
            Optional[User]: 认证成功的用户对象，认证失败则返回 None（如果 raise_exc=False）
            
        Raises:
            HTTPException: 认证失败时抛出401错误（仅当 raise_exc=True 时）
        """
        try:
            if not access_token_str:
                logger.debug("认证失败: 缺少token")
                if raise_exc:
                    raise HTTPException(
                        status_code=401, detail="Missing authentication token"
                    )
                return None

            # 1. 先从 Redis 验证令牌是否存在
            is_valid = token_manager.validate_access_token(access_token_str)
            logger.debug(f"Redis验证令牌结果: {is_valid}")
            
            if not is_valid:
                logger.debug("认证失败: 令牌无效或已撤销")
                if raise_exc:
                    raise HTTPException(status_code=401, detail="令牌已被撤销或失效")
                return None

            # 2. 再验证 JWT（作为额外安全检查）
            decode_data = jwt.decode(
                access_token_str,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            user_id = decode_data.get("user_id")
            logger.debug(f"JWT解码结果: user_id={user_id}")

            with UnitOfWork() as uow:
                from src.models.sys.user import User
                from sqlalchemy import select
                from sqlalchemy.orm import selectinload
                from src.models.sys.role import Role
                
                result = uow.session.execute(
                    select(User)
                    .options(
                        selectinload(User.roles).selectinload(Role.resources)
                    )
                    .where(User.id == user_id)
                )
                user = result.scalars().first()
                logger.debug(f"数据库查询结果: user={user}")

            if not user:
                logger.debug(f"认证失败: 用户不存在 user_id={user_id}")
                if raise_exc:
                    raise HTTPException(status_code=401, detail="Authentication failed")
                return None

            logger.debug(f"设置CTX_USER_ID: {user.id}")
            CTX_USER_ID.set(int(user.id))
            return user
        except jwt.DecodeError as e:
            logger.debug(f"JWT解码错误: {str(e)}")
            if raise_exc:
                raise HTTPException(status_code=401, detail="无效的Token") from e
            return None
        except jwt.ExpiredSignatureError as e:
            logger.debug(f"JWT过期: {str(e)}")
            if raise_exc:
                raise HTTPException(status_code=401, detail="登录已过期") from e
            return None
        except HTTPException:
            if raise_exc:
                raise
            return None
        except Exception as e:
            logger.debug(f"认证异常: {str(e)}")
            if raise_exc:
                raise HTTPException(status_code=401, detail="认证失败") from e
            return None

    @classmethod
    def is_authed(cls, token: HTTPBearer = Depends(bearer_scheme)) -> Optional[object]:
        """验证用户认证状态（用于依赖注入）
        
        Args:
            token: JWT令牌（通过HTTPBearer依赖自动获取）
            
        Returns:
            Optional[User]: 认证成功的用户对象，认证失败则抛出异常
            
        Raises:
            HTTPException: 认证失败时抛出401错误
        """
        logger.debug(f"is_authed 被调用，token credentials = {token.credentials[:50]}...")
        result = cls.authenticate_token(token.credentials)
        logger.debug(f"认证结果: {result}")
        return result
    
    @classmethod
    def get_auth_info(cls, token: HTTPBearer = Depends(bearer_scheme)) -> tuple[Optional[object], str]:
        """验证用户并返回（用户对象，令牌字符串）
        
        Args:
            token: JWT令牌（通过HTTPBearer依赖自动获取）
            
        Returns:
            tuple: (用户对象, 令牌字符串)
            
        Raises:
            HTTPException: 认证失败时抛出401错误
        """
        user = cls.authenticate_token(token.credentials)
        return user, token.credentials


class PermissionControl:
    """权限控制器
    
    处理API权限控制相关的逻辑，检查用户是否有访问指定API的权限。
    """
    
    @classmethod
    def has_permission(
        cls,
        request: Request,
        current_user: object = Depends(AuthControl.is_authed),
    ) -> None:
        """检查用户是否有访问指定API的权限
        
        Args:
            request: FastAPI请求对象
            current_user: 当前认证用户
            
        Raises:
            HTTPException: 当用户无权限时抛出403错误
        """
        method = request.method
        path = request.url.path

        roles = current_user.roles

        if not roles:
            raise HTTPException(
                status_code=403, detail="用户未绑定角色"
            )

        # 超级管理员特殊放行：如果用户有平台超级管理员角色，直接允许
        for role in roles:
            if role.name == "平台超级管理员":
                return

        all_resources = []
        for role in roles:
            all_resources.extend(role.resources)

        for resource in all_resources:
            if resource.api_method == method and resource.api_path is not None:
                pattern = re.sub(r"\{[^}]+\}", r"[^/]+", resource.api_path)
                pattern = f"^{pattern}$"
                if re.match(pattern, path):
                    return

        raise HTTPException(status_code=403, detail="无此API访问权限")

